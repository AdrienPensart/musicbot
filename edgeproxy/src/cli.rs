use clap::Parser;

#[derive(Parser, Debug)]
#[clap(author, about, version)]
pub struct Opts {
    /// Allow insecure mode
    #[arg(long = "insecure", default_value_t = false)]
    pub insecure: bool,

    /// Listening host:port
    #[arg(long = "bind", default_value = "0.0.0.0:8081")]
    pub bind: String,

    /// Basic auth username
    #[arg(long = "username", requires = "password")]
    pub username: Option<String>,

    /// Basic auth password
    #[arg(long = "password", requires = "username")]
    pub password: Option<String>,

    /// Cache duration, 0 to disable
    #[arg(long = "cache-duration", value_parser = humantime::parse_duration, default_value = "60sec")]
    pub cache_duration: Option<std::time::Duration>,

    /// Upstreams EdgeDB endpoints
    #[arg(long = "upstream", num_args=1.., default_values_t = vec!["https://localhost:5656/db/edgedb/edgeql".to_string()])]
    pub upstreams: Vec<String>,
}
