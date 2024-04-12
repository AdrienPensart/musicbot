use thiserror::Error;

#[derive(Debug, Error)]
pub enum EdgeProxyError {
    #[error{"EdgeDB error"}]
    Edgedb(#[from] edgedb_tokio::Error),
    #[error("Missing basic auth username or password")]
    BasicAuth,
}
