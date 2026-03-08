use crate::alliance::{Alliance, AllianceScore};
use ab_glyph::{FontArc, PxScale};
use image::{DynamicImage, Rgb, RgbImage};
use imageproc::drawing::draw_text_mut;

const CANVAS_WIDTH: u32 = 800;
const CANVAS_HEIGHT: u32 = 600;
const BACKGROUND: Rgb<u8> = Rgb([43, 45, 49]); // #2B2D31
const RED: Rgb<u8> = Rgb([237, 28, 36]); // #ED1C24
const BLUE: Rgb<u8> = Rgb([0, 102, 179]); // #0066B3
const PURPLE: Rgb<u8> = Rgb([191, 64, 191]); // #BF40BF
const WHITE: Rgb<u8> = Rgb([255, 255, 255]);
const GRAY: Rgb<u8> = Rgb([154, 152, 154]);

// Embed Roboto font at compile time
const FONT_DATA: &[u8] = include_bytes!("../assets/Roboto-Regular.ttf");

pub struct ImageGenerator;

impl ImageGenerator {
    fn get_font() -> FontArc {
        FontArc::try_from_slice(FONT_DATA).expect("Failed to load embedded font")
    }

    fn truncate_text(text: &str, max_length: usize) -> String {
        if text.len() <= max_length {
            text.to_string()
        } else {
            format!("{}...", &text[..max_length.saturating_sub(3)])
        }
    }

    pub fn create_match_image(red_alliance: &Alliance, blue_alliance: &Alliance) -> DynamicImage {
        let mut img = RgbImage::from_pixel(CANVAS_WIDTH, CANVAS_HEIGHT, BACKGROUND);
        let font = Self::get_font();

        let red_score = red_alliance.calculate_score();
        let blue_score = blue_alliance.calculate_score();
        let red_teams = red_alliance.team_numbers();
        let blue_teams = blue_alliance.team_numbers();
        let red_names = red_alliance.team_names();
        let blue_names = blue_alliance.team_names();

        // Title
        let title = "Simulated Qualification Match";
        draw_text_mut(&mut img, WHITE, 200, 20, PxScale::from(30.0), &font, title);

        // Team numbers subtitle
        let subtitle = format!(
            "{} & {} vs {} & {}",
            red_teams.get(0).unwrap_or(&0),
            red_teams.get(1).unwrap_or(&0),
            blue_teams.get(0).unwrap_or(&0),
            blue_teams.get(1).unwrap_or(&0)
        );
        draw_text_mut(
            &mut img,
            GRAY,
            250,
            55,
            PxScale::from(20.0),
            &font,
            &subtitle,
        );

        // Red alliance section (left)
        draw_text_mut(
            &mut img,
            RED,
            50,
            100,
            PxScale::from(24.0),
            &font,
            "Red Alliance",
        );
        let red_name1 = Self::truncate_text(&red_names[0], 20);
        let red_name2 = Self::truncate_text(&red_names[1], 20);
        draw_text_mut(
            &mut img,
            WHITE,
            50,
            135,
            PxScale::from(18.0),
            &font,
            &red_name1,
        );
        draw_text_mut(
            &mut img,
            WHITE,
            50,
            160,
            PxScale::from(18.0),
            &font,
            &red_name2,
        );

        // Blue alliance section (right)
        draw_text_mut(
            &mut img,
            BLUE,
            580,
            100,
            PxScale::from(24.0),
            &font,
            "Blue Alliance",
        );
        let blue_name1 = Self::truncate_text(&blue_names[0], 20);
        let blue_name2 = Self::truncate_text(&blue_names[1], 20);
        draw_text_mut(
            &mut img,
            WHITE,
            580,
            135,
            PxScale::from(18.0),
            &font,
            &blue_name1,
        );
        draw_text_mut(
            &mut img,
            WHITE,
            580,
            160,
            PxScale::from(18.0),
            &font,
            &blue_name2,
        );

        // Score categories (center)
        draw_text_mut(
            &mut img,
            PURPLE,
            340,
            220,
            PxScale::from(20.0),
            &font,
            "AUTO",
        );
        draw_text_mut(
            &mut img,
            PURPLE,
            330,
            260,
            PxScale::from(20.0),
            &font,
            "TELEOP",
        );
        draw_text_mut(
            &mut img,
            PURPLE,
            320,
            300,
            PxScale::from(20.0),
            &font,
            "ENDGAME",
        );
        draw_text_mut(
            &mut img,
            PURPLE,
            315,
            340,
            PxScale::from(20.0),
            &font,
            "PENALTIES",
        );

        // Red scores (left of center)
        draw_text_mut(
            &mut img,
            RED,
            250,
            220,
            PxScale::from(20.0),
            &font,
            &format!("{:.0}", red_score.auto),
        );
        draw_text_mut(
            &mut img,
            RED,
            250,
            260,
            PxScale::from(20.0),
            &font,
            &format!("{:.0}", red_score.teleop),
        );
        draw_text_mut(
            &mut img,
            RED,
            250,
            300,
            PxScale::from(20.0),
            &font,
            &format!("{:.0}", red_score.endgame),
        );
        draw_text_mut(
            &mut img,
            RED,
            250,
            340,
            PxScale::from(20.0),
            &font,
            &format!("{:.0}", red_score.penalties),
        );

        // Blue scores (right of center)
        draw_text_mut(
            &mut img,
            BLUE,
            480,
            220,
            PxScale::from(20.0),
            &font,
            &format!("{:.0}", blue_score.auto),
        );
        draw_text_mut(
            &mut img,
            BLUE,
            480,
            260,
            PxScale::from(20.0),
            &font,
            &format!("{:.0}", blue_score.teleop),
        );
        draw_text_mut(
            &mut img,
            BLUE,
            480,
            300,
            PxScale::from(20.0),
            &font,
            &format!("{:.0}", blue_score.endgame),
        );
        draw_text_mut(
            &mut img,
            BLUE,
            480,
            340,
            PxScale::from(20.0),
            &font,
            &format!("{:.0}", blue_score.penalties),
        );

        // Final scores
        draw_text_mut(
            &mut img,
            WHITE,
            280,
            450,
            PxScale::from(28.0),
            &font,
            "FINAL SCORE",
        );
        let final_score_text = format!(
            "Red: {:.0}  |  Blue: {:.0}",
            red_score.total, blue_score.total
        );
        draw_text_mut(
            &mut img,
            WHITE,
            250,
            490,
            PxScale::from(24.0),
            &font,
            &final_score_text,
        );

        DynamicImage::ImageRgb8(img)
    }

    pub fn create_alliance_image(alliance: &Alliance) -> DynamicImage {
        let mut img = RgbImage::from_pixel(CANVAS_WIDTH, CANVAS_HEIGHT, BACKGROUND);
        let font = Self::get_font();

        let score = alliance.calculate_score();
        let team_names = alliance.team_names();
        let team_numbers = alliance.team_numbers();

        // Title
        let title = "Simulated Alliance";
        draw_text_mut(&mut img, WHITE, 280, 20, PxScale::from(30.0), &font, title);

        // Team numbers subtitle
        let subtitle = format!(
            "Team {} & Team {}",
            team_numbers.get(0).unwrap_or(&0),
            team_numbers.get(1).unwrap_or(&0)
        );
        draw_text_mut(
            &mut img,
            GRAY,
            300,
            55,
            PxScale::from(20.0),
            &font,
            &subtitle,
        );

        // Column headers
        draw_text_mut(
            &mut img,
            PURPLE,
            100,
            120,
            PxScale::from(22.0),
            &font,
            "Team 1",
        );
        draw_text_mut(
            &mut img,
            PURPLE,
            350,
            120,
            PxScale::from(22.0),
            &font,
            "Category",
        );
        draw_text_mut(
            &mut img,
            PURPLE,
            600,
            120,
            PxScale::from(22.0),
            &font,
            "Team 2",
        );

        // Team names
        let name1 = Self::truncate_text(&team_names[0], 20);
        let name2 = Self::truncate_text(&team_names[1], 20);
        draw_text_mut(
            &mut img,
            WHITE,
            100,
            160,
            PxScale::from(18.0),
            &font,
            &name1,
        );
        draw_text_mut(
            &mut img,
            WHITE,
            600,
            160,
            PxScale::from(18.0),
            &font,
            &name2,
        );

        // Get individual team OPRs
        let team1_auto = alliance.team1.as_ref().map(|t| t.auto_opr).unwrap_or(0.0);
        let team1_tele = alliance.team1.as_ref().map(|t| t.tele_opr).unwrap_or(0.0);
        let team1_endgame = alliance
            .team1
            .as_ref()
            .map(|t| t.endgame_opr)
            .unwrap_or(0.0);
        let team1_total = alliance
            .team1
            .as_ref()
            .map(|t| t.overall_opr)
            .unwrap_or(0.0);

        let team2_auto = alliance.team2.as_ref().map(|t| t.auto_opr).unwrap_or(0.0);
        let team2_tele = alliance.team2.as_ref().map(|t| t.tele_opr).unwrap_or(0.0);
        let team2_endgame = alliance
            .team2
            .as_ref()
            .map(|t| t.endgame_opr)
            .unwrap_or(0.0);
        let team2_total = alliance
            .team2
            .as_ref()
            .map(|t| t.overall_opr)
            .unwrap_or(0.0);

        // OPR rows
        let y_start = 200;
        let y_spacing = 40;

        // Auto OPR
        draw_text_mut(
            &mut img,
            WHITE,
            100,
            y_start,
            PxScale::from(18.0),
            &font,
            &format!("{:.2}", team1_auto),
        );
        draw_text_mut(
            &mut img,
            PURPLE,
            350,
            y_start,
            PxScale::from(18.0),
            &font,
            "Auto OPR",
        );
        draw_text_mut(
            &mut img,
            WHITE,
            600,
            y_start,
            PxScale::from(18.0),
            &font,
            &format!("{:.2}", team2_auto),
        );

        // Teleop OPR
        draw_text_mut(
            &mut img,
            WHITE,
            100,
            y_start + y_spacing,
            PxScale::from(18.0),
            &font,
            &format!("{:.2}", team1_tele),
        );
        draw_text_mut(
            &mut img,
            PURPLE,
            350,
            y_start + y_spacing,
            PxScale::from(18.0),
            &font,
            "Teleop OPR",
        );
        draw_text_mut(
            &mut img,
            WHITE,
            600,
            y_start + y_spacing,
            PxScale::from(18.0),
            &font,
            &format!("{:.2}", team2_tele),
        );

        // Endgame OPR
        draw_text_mut(
            &mut img,
            WHITE,
            100,
            y_start + y_spacing * 2,
            PxScale::from(18.0),
            &font,
            &format!("{:.2}", team1_endgame),
        );
        draw_text_mut(
            &mut img,
            PURPLE,
            350,
            y_start + y_spacing * 2,
            PxScale::from(18.0),
            &font,
            "Endgame OPR",
        );
        draw_text_mut(
            &mut img,
            WHITE,
            600,
            y_start + y_spacing * 2,
            PxScale::from(18.0),
            &font,
            &format!("{:.2}", team2_endgame),
        );

        // Total OPR
        draw_text_mut(
            &mut img,
            WHITE,
            100,
            y_start + y_spacing * 3,
            PxScale::from(18.0),
            &font,
            &format!("{:.2}", team1_total),
        );
        draw_text_mut(
            &mut img,
            PURPLE,
            350,
            y_start + y_spacing * 3,
            PxScale::from(18.0),
            &font,
            "Total OPR",
        );
        draw_text_mut(
            &mut img,
            WHITE,
            600,
            y_start + y_spacing * 3,
            PxScale::from(18.0),
            &font,
            &format!("{:.2}", team2_total),
        );

        // Alliance totals section
        draw_text_mut(
            &mut img,
            PURPLE,
            280,
            420,
            PxScale::from(24.0),
            &font,
            "Alliance Estimated Score",
        );

        draw_text_mut(
            &mut img,
            WHITE,
            200,
            460,
            PxScale::from(18.0),
            &font,
            "AUTO:",
        );
        draw_text_mut(
            &mut img,
            WHITE,
            450,
            460,
            PxScale::from(18.0),
            &font,
            &format!("{:.0}", score.auto),
        );

        draw_text_mut(
            &mut img,
            WHITE,
            200,
            490,
            PxScale::from(18.0),
            &font,
            "TELEOP:",
        );
        draw_text_mut(
            &mut img,
            WHITE,
            450,
            490,
            PxScale::from(18.0),
            &font,
            &format!("{:.0}", score.teleop),
        );

        draw_text_mut(
            &mut img,
            WHITE,
            200,
            520,
            PxScale::from(18.0),
            &font,
            "ENDGAME:",
        );
        draw_text_mut(
            &mut img,
            WHITE,
            450,
            520,
            PxScale::from(18.0),
            &font,
            &format!("{:.0}", score.endgame),
        );

        draw_text_mut(
            &mut img,
            PURPLE,
            250,
            560,
            PxScale::from(22.0),
            &font,
            "TOTAL:",
        );
        draw_text_mut(
            &mut img,
            WHITE,
            450,
            560,
            PxScale::from(22.0),
            &font,
            &format!("{:.0}", score.total),
        );

        DynamicImage::ImageRgb8(img)
    }
}
