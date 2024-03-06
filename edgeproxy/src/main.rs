use auth::create_basic_auth_handler;
use clap::Parser;
use salvo::catcher::Catcher;
use salvo::prelude::*;
use salvo::serve_static::StaticDir;

mod auth;
mod cli;
mod edgify;
mod errors;
mod proxy;

#[tokio::main]
async fn main() {
    let _ = start().await.map_err(|err| eprintln!("{err}"));
}

async fn start() -> Result<(), crate::errors::EdgeProxyError> {
    tracing_subscriber::fmt().init();
    let opts = crate::cli::Opts::parse();
    let proxy = crate::proxy::create_proxy(opts.upstreams, opts.insecure)?;

    let router = match (opts.username, opts.password) {
        (None, None) => Router::new(),
        (Some(username), Some(password)) => {
            let auth_handler = create_basic_auth_handler(username.as_str(), password.as_str());
            Router::with_hoop(auth_handler)
        }
        _ => return Err(crate::errors::EdgeProxyError::BasicAuthError),
    }
    .hoop(Logger::new());

    let artists = crate::edgify::Edgify::new("artists", "select Artist {*}", opts.cache_duration);
    let index = Router::with_path("<**path>").get(
        StaticDir::new(["static"])
            .defaults("index.html")
            .auto_list(false),
    );

    let mut routes = vec![artists.router().get(proxy), index];
    let edgeproxy = router.append(&mut routes);
    let catcher = Catcher::default();
    let service = Service::new(edgeproxy).catcher(catcher);
    let acceptor = TcpListener::new(opts.bind).bind().await;
    Server::new(acceptor).serve(service).await;
    Ok(())
}
