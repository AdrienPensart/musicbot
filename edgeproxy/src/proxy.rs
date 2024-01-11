use crate::errors::EdgeProxyError;
use hyper_tls::HttpsConnector;
use hyper_util::client::legacy::connect::HttpConnector;
use hyper_util::client::legacy::Client as HyperUtilClient;
use salvo::proxy::{HyperClient, Proxy};

pub fn create_proxy<U>(
    upstreams: U,
    insecure: bool,
) -> Result<Proxy<U, HyperClient>, EdgeProxyError>
where
    U: salvo::proxy::Upstreams,
{
    if !insecure {
        return Ok(Proxy::default_hyper_client(upstreams));
    }
    let mut http_connector = HttpConnector::new();
    http_connector.enforce_http(false);

    let native_tls_connector = native_tls::TlsConnector::builder()
        .danger_accept_invalid_certs(true)
        .build()?;

    let tls_connector = tokio_native_tls::TlsConnector::from(native_tls_connector);
    let connector = HttpsConnector::from((http_connector, tls_connector));

    let proxy = Proxy::new(
        upstreams,
        HyperClient::new(
            HyperUtilClient::builder(salvo::rt::tokio::TokioExecutor::new()).build(connector),
        ),
    );
    Ok(proxy)
}
