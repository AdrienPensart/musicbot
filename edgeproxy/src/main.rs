use crate::edgify::Edgify;
use crate::errors::EdgeProxyError;
use auth::create_basic_auth_handler;
use clap::Parser;

use salvo::catcher::Catcher;
use salvo::prelude::*;
use salvo::serve_static::StaticDir;

mod auth;
mod cli;
mod edgify;
mod errors;

#[tokio::main]
async fn main() {
    let _ = start().await.map_err(|err| eprintln!("{err}"));
}

async fn start() -> Result<(), EdgeProxyError> {
    tracing_subscriber::fmt().init();

    let opts = crate::cli::Opts::parse();

    let conn = edgedb_tokio::Client::new(
        &edgedb_tokio::Builder::new()
            .dsn("edgedb://musicbot:musicbot@127.0.0.1:5656?tls_security=insecure")?
            .build_env()
            .await?,
    );
    conn.ensure_connected().await?;
    edgify::EDGEDB_POOL.set(conn).ok();

    // let proxy = crate::proxy::create_proxy(opts.upstreams, opts.insecure)?;

    let router = match (opts.username, opts.password) {
        (None, None) => Router::new(),
        (Some(username), Some(password)) => {
            let auth_handler = create_basic_auth_handler(username.as_str(), password.as_str());
            Router::with_hoop(auth_handler)
        }
        _ => return Err(EdgeProxyError::BasicAuth),
    }
    .hoop(Logger::new());

    // let artists = crate::edgify::Edgify::new("artists", "select Artist {*}", opts.cache_duration);

    let index = Router::with_path("<**path>").get(
        StaticDir::new(["static"])
            .defaults("index.html")
            .auto_list(false),
    );

    let mut routes = vec![
        Edgify::new("artists", "select Artist {*}", opts.cache_duration).router(),
        Edgify::new("albums", "select Album {*}", opts.cache_duration).router(),
        Edgify::new("genres", "select Genre {*}", opts.cache_duration).router(),
        Edgify::new("musics", "select Music {*}", opts.cache_duration).router(),
        Edgify::new("keywords", "select Keyword {*}", opts.cache_duration).router(),
        Edgify::new("folders", "select Folder {*}", opts.cache_duration).router(),
        index,
    ];
    let edgeproxy = router.append(&mut routes);
    let catcher = Catcher::default();
    let service = Service::new(edgeproxy).catcher(catcher);

    let acceptor = TcpListener::new(opts.bind).bind().await;
    Server::new(acceptor).serve(service).await;
    Ok(())
}
