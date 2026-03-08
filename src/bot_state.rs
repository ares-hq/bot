use serenity::all::{Colour, CreateEmbed, Timestamp};

// Visual helper constants shared by command modules.
pub const VERSION: &str = concat!("v", env!("CARGO_PKG_VERSION"));
pub const NAME: &str = "ARES";
pub const DEVELOPERS: &str = "<@291420737204649985> and <@751915057973035058>";
pub const CHANNELS: &[&str] = &["bot", "bot-channel", "ares", "scout", "ftc", "general"];
pub const PRESENCE: &str = "Decode 🧭";

pub struct Colors;

impl Colors {
    // COLOR SOURCE:
    // https://www.firstinspires.org/sites/default/files/uploads/resource_library/brand/first-brand-guidelines-2020.pdf

    // CORE COLOR PALETTE
    pub const FIRST_BLACK: Colour = Colour::new(0x231F20);
    pub const FIRST_BLUE: Colour = Colour::new(0x0066B3);
    pub const FIRST_GRAY: Colour = Colour::new(0x9A989A);

    // LEAGUE-SPECIFIC COLOR PALETTE
    // FIRST LEGO LEAGUE
    pub const DISCOVER_PURPLE: Colour = Colour::new(0x662D91);
    pub const EXPLORE_GREEN: Colour = Colour::new(0x00A651);
    pub const CHALLENGE_RED: Colour = Colour::new(0xED1C24);
    // FIRST TECH CHALLENGE
    pub const TECH_ORANGE: Colour = Colour::new(0xF57E25);
    // FIRST ROBOTICS COMPETITION
    pub const ROBOT_BLUE: Colour = Colour::new(0x009CD7);

    // CUSTOM COLOR PALETTE
    pub const WHITE: Colour = Colour::new(0xFFFFFF);
    pub const FAVORITE: Colour = Colour::new(0xFFD700);
}

pub fn error_embed(title: &str, description: &str) -> CreateEmbed {
    CreateEmbed::new()
        .title(title)
        .description(description)
        .color(Colors::CHALLENGE_RED)
        .timestamp(Timestamp::now())
}

pub fn success_embed(title: &str, description: &str) -> CreateEmbed {
    CreateEmbed::new()
        .title(title)
        .description(description)
        .color(Colors::EXPLORE_GREEN)
        .timestamp(Timestamp::now())
}

pub fn warning_embed(title: &str, description: &str) -> CreateEmbed {
    CreateEmbed::new()
        .title(title)
        .description(description)
        .color(Colors::TECH_ORANGE)
        .timestamp(Timestamp::now())
}

pub fn info_embed(title: &str, description: &str) -> CreateEmbed {
    CreateEmbed::new()
        .title(title)
        .description(description)
        .color(Colors::FIRST_BLUE)
        .timestamp(Timestamp::now())
}

pub fn announcement_embed(title: &str, description: &str) -> CreateEmbed {
    CreateEmbed::new()
        .title(title)
        .description(description)
        .color(Colour::TEAL)
        .timestamp(Timestamp::now())
}
