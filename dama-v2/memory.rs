/// Episodic Working Memory: Stack-allocated fixed-size ring buffer with 
/// natural recurrent scaling for gradient guidance and trajectory tracking.
#[derive(Debug, Clone, Copy)]
pub struct RingBuffer<T, const CAPACITY: usize> {
    pub data: [T; CAPACITY],
    pub head: usize,
    pub len: usize,
}

impl<T: Copy + Default, const CAPACITY: usize> RingBuffer<T, CAPACITY> {
    /// Initialize an empty ring buffer with a compile-time capacity.
    pub fn new() -> Self {
        Self {
            data: [T::default(); CAPACITY],
            head: 0,
            len: 0,
        }
    }

    /// Push a new state snapshot into the buffer, overwriting the oldest if full.
    pub fn push(&mut self, item: T) {
        self.data[self.head] = item;
        self.head = (self.head + 1) % CAPACITY;
        if self.len < CAPACITY {
            self.len += 1;
        }
    }

    /// Retrieve a historical snapshot by relative index (0 = oldest in window, len-1 = newest).
    pub fn get(&self, index: usize) -> Option<&T> {
        if index >= self.len {
            return None;
        }
        let real_idx = if self.len < CAPACITY {
            index
        } else {
            (self.head + index) % CAPACITY
        };
        Some(&self.data[real_idx])
    }

    /// Computes a recurrent weighted fold over the history buffer using a decay factor alpha.
    pub fn fold_recurrent<F, Accumulator>(&self, initial: Accumulator, mut folder: F) -> Accumulator
    where
        F: FnMut(Accumulator, &T, f64) -> Accumulator,
    {
        let mut acc = initial;
        let alpha: f64 = 0.85; // Natural recurrent decay factor

        for i in 0..self.len {
            if let Some(item) = self.get(i) {
                let age = (self.len - 1 - i) as i32;
                let weight = alpha.powi(age);
                acc = folder(acc, item, weight);
            }
        }
        acc
    }
}