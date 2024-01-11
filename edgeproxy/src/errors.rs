use thiserror::Error;

#[derive(Debug, Error)]
pub enum EdgeProxyError {
    #[error("TLS error")]
    TlsError(#[from] native_tls::Error),
    #[error("Missing basic auth username or password")]
    BasicAuthError,
}
