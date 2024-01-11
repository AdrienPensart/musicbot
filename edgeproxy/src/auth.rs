use salvo::basic_auth::{BasicAuth, BasicAuthValidator};
use salvo::prelude::*;

pub struct Validator {
    username: String,
    password: String,
}

#[async_trait]
impl BasicAuthValidator for Validator {
    async fn validate(&self, username: &str, password: &str, _depot: &mut Depot) -> bool {
        username == self.username && password == self.password
    }
}

pub fn create_basic_auth_handler(username: &str, password: &str) -> BasicAuth<Validator> {
    let validator = Validator {
        username: username.into(),
        password: password.into(),
    };
    BasicAuth::new(validator)
}
