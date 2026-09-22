use crate::alliance::Alliance;
use anyhow::{Context, Result, anyhow};
use askama::Template;
use model::prelude::{Alliance as Scores, Match as Scored, Team, Winner};
use resvg::tiny_skia::{Pixmap, Transform};
use resvg::usvg::{Options, Tree, fontdb};
use std::sync::{Arc, LazyLock};

const W: u32 = 1000;
const H: u32 = 600;

static FONTS: LazyLock<Arc<fontdb::Database>> = LazyLock::new(|| {
    let mut db = fontdb::Database::new();
    for ttf in [
        include_bytes!("../assets/Rajdhani-Medium.ttf").as_slice(),
        include_bytes!("../assets/Rajdhani-SemiBold.ttf"),
        include_bytes!("../assets/Rajdhani-Bold.ttf"),
        include_bytes!("../assets/Roboto-Regular.ttf"),
    ] {
        db.load_font_data(ttf.to_vec());
    }
    Arc::new(db)
});

const RED: &str = "#FF4B55";
const BLUE: &str = "#3D8BFF";
const DIM: &str = "#6E7480";
const STROKE: &str = "#2E333C";

struct TeamLine {
    y: f64,
    num: String,
    name: String,
}

struct BarRow {
    label: &'static str,
    ly: f64,
    y: f64,
    vy: f64,
    rx: f64,
    rw: f64,
    bw: f64,
    rtx: f64,
    btx: f64,
    red_fill: &'static str,
    blue_fill: &'static str,
    red_color: &'static str,
    blue_color: &'static str,
    red_val: String,
    blue_val: String,
}

#[derive(Template)]
#[template(path = "match_card.svg", escape = "html")]
struct MatchCard {
    r0: String,
    r1: String,
    b0: String,
    b1: String,
    red_win: bool,
    blue_win: bool,
    red_stroke: &'static str,
    blue_stroke: &'static str,
    red_total_col: &'static str,
    blue_total_col: &'static str,
    r_total: String,
    b_total: String,
    red_lines: Vec<TeamLine>,
    blue_lines: Vec<TeamLine>,
    rows: Vec<BarRow>,
}

struct TeamHeader {
    x: f64,
    num: String,
    name: String,
}

struct OprRow {
    label: &'static str,
    y: f64,
    t1: String,
    t2: String,
}

#[derive(Template)]
#[template(path = "alliance_card.svg", escape = "html")]
struct AllianceCard {
    subtitle_a: String,
    subtitle_b: String,
    headers: Vec<TeamHeader>,
    rows: Vec<OprRow>,
    auto: String,
    teleop: String,
    total: String,
}

pub struct ImageGenerator;

impl ImageGenerator {
    pub fn create_match_image(red: &Alliance, blue: &Alliance) -> Result<Vec<u8>> {
        let (r, b): (Scores, Scores) = (red.into(), blue.into());
        let scored = Scored::new(r.clone(), b.clone());
        let (r_total, b_total) = scored.totals();
        let winner = scored.winner();
        let red_win = winner == Some(Winner::Red);
        let blue_win = winner == Some(Winner::Blue);

        let scale = 360.0
            / [
                r.auto,
                b.auto,
                r.teleop,
                b.teleop,
                r.endgame,
                b.endgame,
                r.penalties,
                b.penalties,
            ]
            .into_iter()
            .fold(1.0_f64, f64::max);

        let rows = vec![
            bar_row("AUTO", r.auto, b.auto, RED, BLUE, 386.0, scale),
            bar_row("TELEOP", r.teleop, b.teleop, RED, BLUE, 432.0, scale),
            bar_row("ENDGAME", r.endgame, b.endgame, RED, BLUE, 478.0, scale),
            bar_row(
                "PENALTIES",
                b.penalties,
                r.penalties,
                BLUE,
                RED,
                524.0,
                scale,
            ),
        ];

        let card = MatchCard {
            r0: slot_num(red, 0),
            r1: slot_num(red, 1),
            b0: slot_num(blue, 0),
            b1: slot_num(blue, 1),
            red_win,
            blue_win,
            red_stroke: if red_win { RED } else { STROKE },
            blue_stroke: if blue_win { BLUE } else { STROKE },
            red_total_col: if blue_win { DIM } else { RED },
            blue_total_col: if red_win { DIM } else { BLUE },
            r_total: format!("{r_total:.0}"),
            b_total: format!("{b_total:.0}"),
            red_lines: vec![team_line(red, 0, 196.0), team_line(red, 1, 226.0)],
            blue_lines: vec![team_line(blue, 0, 196.0), team_line(blue, 1, 226.0)],
            rows,
        };
        render(&card.render().context("rendering match card template")?)
    }

    pub fn create_alliance_image(alliance: &Alliance) -> Result<Vec<u8>> {
        let s = Scores::from(alliance);
        let t1 = alliance.team(0);
        let t2 = alliance.team(1);
        let opr = |team: Option<&Team>, pick: fn(&Team) -> f64| team.map(pick).unwrap_or(0.0);

        let rows = vec![
            opr_row("AUTO OPR", opr(t1, |t| t.auto), opr(t2, |t| t.auto), 250.0),
            opr_row(
                "TELEOP OPR",
                opr(t1, |t| t.teleop),
                opr(t2, |t| t.teleop),
                296.0,
            ),
            opr_row(
                "ENDGAME OPR",
                opr(t1, |t| t.endgame),
                opr(t2, |t| t.endgame),
                342.0,
            ),
            opr_row(
                "TOTAL OPR",
                opr(t1, |t| t.overall),
                opr(t2, |t| t.overall),
                388.0,
            ),
        ];

        let card = AllianceCard {
            subtitle_a: slot_num(alliance, 0),
            subtitle_b: slot_num(alliance, 1),
            headers: vec![
                team_header(alliance, 0, 200.0),
                team_header(alliance, 1, 800.0),
            ],
            rows,
            auto: format!("{:.0}", s.auto),
            teleop: format!("{:.0}", s.teleop),
            total: format!("{:.0}", s.points()),
        };
        render(&card.render().context("rendering alliance card template")?)
    }
}

fn render(svg: &str) -> Result<Vec<u8>> {
    let opt = Options {
        fontdb: FONTS.clone(),
        ..Default::default()
    };
    let tree = Tree::from_str(svg, &opt).context("parsing card SVG")?;
    let mut pixmap = Pixmap::new(W, H).ok_or_else(|| anyhow!("cannot allocate {W}x{H} pixmap"))?;
    resvg::render(&tree, Transform::identity(), &mut pixmap.as_mut());
    pixmap.encode_png().context("encoding card PNG")
}

fn bar_row(
    label: &'static str,
    left_val: f64,
    right_val: f64,
    left_color: &'static str,
    right_color: &'static str,
    y: f64,
    scale: f64,
) -> BarRow {
    let rw = (left_val.max(0.0) * scale).min(360.0);
    let bw = (right_val.max(0.0) * scale).min(360.0);
    let fill = |c: &str| {
        if c == RED {
            "url(#redfill)"
        } else {
            "url(#bluefill)"
        }
    };
    BarRow {
        label,
        ly: y - 8.0,
        y,
        vy: y + 11.0,
        rx: 500.0 - rw,
        rw,
        bw,
        rtx: 500.0 - rw - 12.0,
        btx: 500.0 + bw + 12.0,
        red_fill: fill(left_color),
        blue_fill: fill(right_color),
        red_color: left_color,
        blue_color: right_color,
        red_val: format!("{left_val:.0}"),
        blue_val: format!("{right_val:.0}"),
    }
}

fn opr_row(label: &'static str, t1: f64, t2: f64, y: f64) -> OprRow {
    OprRow {
        label,
        y,
        t1: format!("{t1:.2}"),
        t2: format!("{t2:.2}"),
    }
}

fn team_line(alliance: &Alliance, slot: usize, y: f64) -> TeamLine {
    let (num, name) = slot_parts(alliance, slot, 22);
    TeamLine { y, num, name }
}

fn team_header(alliance: &Alliance, slot: usize, x: f64) -> TeamHeader {
    let (num, name) = slot_parts(alliance, slot, 20);
    TeamHeader { x, num, name }
}

fn slot_parts(alliance: &Alliance, slot: usize, max: usize) -> (String, String) {
    let name = alliance
        .team(slot)
        .map_or_else(|| "Empty".to_string(), |t| trunc(&t.name, max));
    (slot_num(alliance, slot), name)
}

fn slot_num(alliance: &Alliance, slot: usize) -> String {
    alliance
        .team(slot)
        .map_or_else(|| "—".to_string(), |t| t.number.to_string())
}

fn trunc(s: &str, n: usize) -> String {
    if s.chars().count() <= n {
        s.to_string()
    } else {
        let kept: String = s.chars().take(n.saturating_sub(1)).collect();
        format!("{kept}…")
    }
}

#[cfg(test)]
mod smoke {
    use super::*;
    use crate::alliance::Alliance;
    use model::prelude::Team;

    fn team(n: u32, name: &str, a: f64, t: f64, e: f64, p: f64) -> Team {
        let mut tm = Team::new(n, name.to_string());
        tm.auto = a;
        tm.teleop = t;
        tm.endgame = e;
        tm.penalties = p;
        tm.recompute_overall();
        tm
    }

    #[test]
    fn render_sample() {
        let red = Alliance::new(
            Some(team(12345, "Robo Raiders", 22.0, 44.0, 15.0, 5.0)),
            Some(team(6789, "Circuit Breakers", 23.0, 44.0, 15.0, 0.0)),
        );
        let blue = Alliance::new(
            Some(team(4321, "Gear Grinders", 19.0, 48.0, 10.0, 8.0)),
            Some(team(9876, "Volt Vipers", 19.0, 47.0, 10.0, 7.0)),
        );
        let png = ImageGenerator::create_match_image(&red, &blue).unwrap();
        assert_eq!(&png[1..4], b"PNG");
        assert!(png.len() > 1000);
    }
}
