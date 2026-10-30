use chrono::{DateTime, Utc};
use std::collections::{BTreeSet, HashMap};
use std::hash::Hash;

/// At most one pending wake per key.
pub struct Timers<K> {
    queue: BTreeSet<(DateTime<Utc>, K)>,
    due: HashMap<K, DateTime<Utc>>,
}

impl<K> Default for Timers<K> {
    fn default() -> Self {
        Self {
            queue: BTreeSet::new(),
            due: HashMap::new(),
        }
    }
}

impl<K: Ord + Hash + Clone> Timers<K> {
    pub fn set(&mut self, key: K, at: DateTime<Utc>) {
        if let Some(old) = self.due.insert(key.clone(), at) {
            self.queue.remove(&(old, key.clone()));
        }
        self.queue.insert((at, key));
    }

    pub fn cancel(&mut self, key: &K) {
        if let Some(at) = self.due.remove(key) {
            self.queue.remove(&(at, key.clone()));
        }
    }

    pub fn contains(&self, key: &K) -> bool {
        self.due.contains_key(key)
    }

    pub fn next(&self) -> Option<DateTime<Utc>> {
        self.queue.first().map(|(at, _)| *at)
    }

    pub fn pop_due(&mut self, now: DateTime<Utc>) -> Vec<K> {
        let mut due = Vec::new();
        while self.queue.first().is_some_and(|(at, _)| *at <= now) {
            if let Some((_, key)) = self.queue.pop_first() {
                self.due.remove(&key);
                due.push(key);
            }
        }
        due
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::TimeDelta;

    fn at(minutes: i64) -> DateTime<Utc> {
        DateTime::UNIX_EPOCH + TimeDelta::minutes(minutes)
    }

    #[test]
    fn keys_pop_in_due_order_and_only_once_due() {
        let mut t = Timers::default();
        t.set("b", at(2));
        t.set("a", at(1));
        t.set("c", at(9));
        assert_eq!(t.pop_due(at(5)), ["a", "b"]);
        assert_eq!(t.next(), Some(at(9)));
    }

    #[test]
    fn setting_again_replaces_the_pending_wake() {
        let mut t = Timers::default();
        t.set("a", at(1));
        t.set("a", at(7));
        assert!(t.pop_due(at(5)).is_empty());
        assert_eq!(t.pop_due(at(7)), ["a"]);
        assert_eq!(t.next(), None);
    }

    #[test]
    fn a_cancelled_key_never_fires() {
        let mut t = Timers::default();
        t.set("a", at(1));
        t.cancel(&"a");
        assert!(t.pop_due(at(5)).is_empty());
    }
}
