use http_body_util::BodyExt;
use salvo::cache::{Cache, MokaStore, RequestIssuer};
use salvo::core::http::header::{HeaderValue, CONTENT_LENGTH, CONTENT_TYPE};
use salvo::http::Method;
// use salvo::logging::Logger;
use salvo::prelude::*;
use std::time::Duration;
use tracing::{debug, info, warn};

#[derive(Debug)]
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
                MokaStore::builder().time_to_live(cache_duration).build(),
                RequestIssuer::default(),
            );
            router = router.hoop(cache);
        };
        info!("{self:?} registered");
        // router.hoop(self).hoop(Logger::new())
        router.hoop(self)
    }
}

#[async_trait]
impl Handler for Edgify {
    async fn handle(
        &self,
        req: &mut Request,
        depot: &mut Depot,
        res: &mut Response,
        ctrl: &mut FlowCtrl,
    ) {
        debug!("incoming request: {:?}", req);
        let query = self.query.clone();
        *req.method_mut() = Method::POST;
        *req.body_mut() = query.into();
        req.headers_mut()
            .insert(CONTENT_TYPE, HeaderValue::from_static("application/json"));
        req.headers_mut()
            .insert(CONTENT_LENGTH, HeaderValue::from(self.query.len()));

        debug!("outgoing request: {:?}", req);
        ctrl.call_next(req, depot, res).await;
        debug!("incoming response: {:?}", res);

        if self.cache_duration.is_some() {
            match res.take_body() {
                salvo::http::ResBody::Hyper(incoming) => {
                    // this will ensure response is cached
                    let body = incoming.collect().await.unwrap();
                    res.replace_body(salvo::http::ResBody::Once(body.to_bytes()));
                }
                _ => {
                    warn!("{req:?} has uncachable body");
                }
            }
        }
        debug!("outgoing response: {:?}", res);
    }
}
