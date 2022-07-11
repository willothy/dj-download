use yew::{prelude, function_component, Html, html};

fn main() {
    yew::start_app::<App>();
}

#[function_component(App)]
pub fn app() -> Html {
    html! {
        <div>
            <h1 class={"heading"}>{"Hello, world!"}</h1>
        </div>
    }
}