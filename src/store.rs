use serenity::model::id::ChannelId;
use std::num::NonZeroU64;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Placement {
    Added,
    Moved,
    Unchanged,
}

impl Placement {
    pub fn decide(current: Option<Option<ChannelId>>, channel: ChannelId) -> Self {
        match current {
            None => Placement::Added,
            Some(Some(existing)) if existing == channel => Placement::Unchanged,
            Some(_) => Placement::Moved,
        }
    }
}

/// Discord ids are stored as text; `0` and garbage are rejected.
pub fn parse_id<T: From<NonZeroU64>>(raw: &str) -> Option<T> {
    raw.parse().ok().and_then(NonZeroU64::new).map(T::from)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serenity::model::id::GuildId;

    const HERE: ChannelId = ChannelId::new(1);
    const ELSEWHERE: ChannelId = ChannelId::new(2);

    #[test]
    fn an_absent_entry_is_added() {
        assert_eq!(Placement::decide(None, HERE), Placement::Added);
    }

    #[test]
    fn the_same_channel_changes_nothing() {
        assert_eq!(
            Placement::decide(Some(Some(HERE)), HERE),
            Placement::Unchanged
        );
    }

    #[test]
    fn another_channel_moves() {
        assert_eq!(
            Placement::decide(Some(Some(ELSEWHERE)), HERE),
            Placement::Moved
        );
    }

    #[test]
    fn a_favorite_without_a_channel_gains_one() {
        assert_eq!(Placement::decide(Some(None), HERE), Placement::Moved);
    }

    #[test]
    fn ids_parse_from_text_and_reject_zero() {
        assert_eq!(parse_id::<GuildId>("42"), Some(GuildId::new(42)));
        assert_eq!(parse_id::<GuildId>("0"), None);
        assert_eq!(parse_id::<GuildId>("abc"), None);
    }
}
