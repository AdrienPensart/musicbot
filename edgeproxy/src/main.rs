use std::time::Duration;
use salvo::prelude::*;
use salvo::logging::Logger;
use salvo::proxy::Proxy;
use salvo::http::Method;
use salvo::cache::{Cache, MokaStore, RequestIssuer};
use salvo::basic_auth::{BasicAuth, BasicAuthValidator};
use salvo::core::http::header::{HeaderValue, CONTENT_TYPE, CONTENT_LENGTH};
use salvo::core::http::ResBody;
use salvo::serve_static::StaticDir;
use bytes::BytesMut;
use futures_util::stream::StreamExt;

pub struct Edgify {
    path: String,
    query: String,
    cache_duration: Option<Duration>,
}

impl Edgify {
    pub fn new(path: &str, query: &str, cache_duration: Option<Duration>) -> Self {
        let query = format!(r#"{{"query": "{}"}}"#, query);
        Self {
            path: path.into(),
            query,
            cache_duration,
        }
    }
    pub fn router(self) -> Router {
        let mut router = Router::with_path(self.path.clone());

        if let Some(cache_duration) = self.cache_duration {
            let cache = Cache::new(
                MokaStore::builder()
                    .time_to_live(cache_duration)
                    .build(),
                RequestIssuer::default(),
            );
            router = router.hoop(cache);
        };
        router
            .hoop(self)
            .hoop(Logger::new())
    }
}

#[async_trait]
impl Handler for Edgify {
    async fn handle(&self, req: &mut Request, depot: &mut Depot, res: &mut Response, ctrl: &mut FlowCtrl) {
        *req.method_mut() = Method::POST;
        *req.body_mut() = self.query.clone().into();
        req.headers_mut().insert(CONTENT_TYPE, HeaderValue::from_static("application/json"));

        ctrl.call_next(req, depot, res).await;

        if let ResBody::Stream(mut stream) = res.take_body() {
            let mut result = BytesMut::new();
            while let Some(Ok(data)) = stream.next().await {
                result.extend_from_slice(&data)
            }
            let length = result.len();
            res.write_body(result).ok();
            res.headers_mut().insert(CONTENT_LENGTH, HeaderValue::from(length));
        }
    }
}

struct Validator
{
    username: String,
    password: String,
}

#[async_trait]
impl BasicAuthValidator for Validator {
    async fn validate(&self, username: &str, password: &str, _depot: &mut Depot) -> bool {
        username == self.username && password == self.password
    }
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt().init();
    let upstream = ["http://localhost:10701/db/edgedb/edgeql"];

    let proxy = Proxy::new(upstream);
    let acceptor = TcpListener::new("0.0.0.0:8081").bind().await;
    let artists = Edgify::new(
        "artists",
        "select artists {*}",
        Some(Duration::from_secs(60)),
    );
    let validator = Validator {
        username: "crunch".into(),
        password: "musicbot".into(),
    };
    let auth_handler = BasicAuth::new(validator);
    let router = Router::with_hoop(auth_handler)
        .push(
            artists.router().get(proxy)
        )
        .push(
            Router::with_path("<**path>").get(
                StaticDir::new([
                    "static",
                ])
                .defaults("index.html")
                .listing(false),
            )
        );
    Server::new(acceptor).serve(router).await;
}
