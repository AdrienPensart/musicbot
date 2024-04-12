use once_cell::sync::OnceCell;
use salvo::cache::{Cache, MokaStore, RequestIssuer};
use salvo::prelude::*;
use std::time::Duration;
use tracing::info;

pub static EDGEDB_POOL: OnceCell<edgedb_tokio::Client> = OnceCell::new();

#[derive(Debug)]
pub struct Edgify {
    path: String,
    query: String,
    cache_duration: Option<Duration>,
}

impl Edgify {
    pub fn new(path: &str, query: &str, cache_duration: Option<Duration>) -> Self {
        Self {
            path: path.into(),
            query: query.into(),
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
        router.get(self)
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
        let Some(client) = EDGEDB_POOL.get() else {
            res.status_code(StatusCode::INTERNAL_SERVER_ERROR);
            res.render("bad edgedb conn");
            ctrl.skip_rest();
            return;
        };

        match client.query_json(self.query.as_str(), &()).await {
            Err(e) => {
                res.status_code(StatusCode::INTERNAL_SERVER_ERROR);
                res.render(e.to_string());
                ctrl.skip_rest();
                return;
            }
            Ok(result) => {
                res.render(Text::Json(result.to_string()));
                ctrl.call_next(req, depot, res).await;
            }
        };
    }
}
