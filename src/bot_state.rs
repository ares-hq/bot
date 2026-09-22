use serenity::all::{Colour, CreateEmbed, Timestamp};

pub const VERSION: &str = concat!("v", env!("CARGO_PKG_VERSION"));
pub const NAME: &str = "ARES";
pub const DEVELOPERS: &str = "<@291420737204649985> and <@751915057973035058>";
pub const PRESENCE: &str = "Biobuzz 🐝";

pub struct Colors;

/// https://www.firstinspires.org/sites/default/files/uploads/resource_library/brand/first-brand-guidelines-2020.pdf
#[allow(dead_code)]
impl Colors {
    // CORE
    pub const FIRST_BLACK: Colour = Colour::new(0x231F20);
    pub const FIRST_BLUE: Colour = Colour::new(0x0066B3);
    pub const FIRST_GRAY: Colour = Colour::new(0x9A989A);

    // FIRST LEGO LEAGUE
    pub const DISCOVER_PURPLE: Colour = Colour::new(0x662D91);
    pub const EXPLORE_GREEN: Colour = Colour::new(0x00A651);
    pub const CHALLENGE_RED: Colour = Colour::new(0xED1C24);

    // FIRST TECH CHALLENGE
    pub const TECH_ORANGE: Colour = Colour::new(0xF57E25);

    // FIRST ROBOTICS COMPETITION
    pub const ROBOT_BLUE: Colour = Colour::new(0x009CD7);

    // CUSTOM
    pub const WHITE: Colour = Colour::new(0xFFFFFF);
    pub const FAVORITE: Colour = Colour::new(0xFFD700);
}

fn embed(title: &str, description: &str, color: Colour) -> CreateEmbed {
    CreateEmbed::new()
        .title(title)
        .description(description)
        .color(color)
        .timestamp(Timestamp::now())
}

pub fn error_embed(title: &str, description: &str) -> CreateEmbed {
    embed(title, description, Colors::CHALLENGE_RED)
}

pub fn success_embed(title: &str, description: &str) -> CreateEmbed {
    embed(title, description, Colors::EXPLORE_GREEN)
}

pub fn warning_embed(title: &str, description: &str) -> CreateEmbed {
    embed(title, description, Colors::TECH_ORANGE)
}
