use std::borrow;

use include_dir::{include_dir, Dir};
use liquid::Template;

use super::liquid_exts::{CompactPathlikeFilterParser, FileExtFilterParser, JsonFilterParser, StripPrefixOrEmptyFilterParser, EnsureBugUrlFilterParser};

static TEMPLATE_DIR: Dir = include_dir!("$CARGO_MANIFEST_DIR/templates");

#[derive(Default, Debug, Clone, Copy)]
struct StaticTemplateSource;

impl liquid::partials::PartialSource for StaticTemplateSource {
    fn contains(&self, _name: &str) -> bool {
        true
    }

    fn names(&self) -> Vec<&str> {
        vec![]
    }

    fn try_get<'a>(&'a self, name: &str) -> Option<borrow::Cow<'a, str>> {
        match TEMPLATE_DIR.get_file(name) {
            Some(file) => file.contents_utf8().map(|s| borrow::Cow::from(s)),
            _ => None,
        }
    }
}

pub fn build_and_parse(s: &str) -> Template {
    liquid::ParserBuilder::with_stdlib()
        .filter(CompactPathlikeFilterParser)
        .filter(EnsureBugUrlFilterParser)
        .filter(FileExtFilterParser)
        .filter(JsonFilterParser)
        .filter(StripPrefixOrEmptyFilterParser)
        .partials(liquid::partials::LazyCompiler::<StaticTemplateSource>::empty())
        .build()
        .expect("Problem building the liquid template")
        .parse(s)
        .expect("Problem parsing the liquid template")
}

pub fn build_and_parse_pipeline_explainer() -> Template {
    let template_str = TEMPLATE_DIR
        .get_file("pipeline_explainer.liquid")
        .unwrap()
        .contents_utf8()
        .unwrap();
    build_and_parse(template_str)
}

pub fn build_and_parse_query_results() -> Template {
    let template_str = TEMPLATE_DIR
        .get_file("query_results.liquid")
        .unwrap()
        .contents_utf8()
        .unwrap();
    build_and_parse(template_str)
}

pub fn build_and_parse_dir_listing() -> Template {
    let template_str = TEMPLATE_DIR
        .get_file("dir_listing.liquid")
        .unwrap()
        .contents_utf8()
        .unwrap();
    build_and_parse(template_str)
}
