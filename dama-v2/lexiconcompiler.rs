use crate::topology::SemanticOperator;
use crate::engine::Command;
use crate::chronon::Chronon;

pub struct LexiconCompiler;

impl LexiconCompiler {
    /// Compiles a text stream into a sequence of engine commands and global token triggers
    pub fn compile_text(input: &str) -> Vec<Command> {
        let raw_tokens: Vec<String> = input
            .split_whitespace()
            .map(|s| s.to_string())
            .collect();

        let mut commands = Vec::new();
        let default_chronon = Chronon::new(1, 1);
        let mut active_phrase_tokens = Vec::new();

        for token in raw_tokens {
            let lower = token.to_lowercase();
            active_phrase_tokens.push(token.clone());

            match lower.as_str() {
                "refrak" => commands.push(Command::InjectOp(0, SemanticOperator::Refrak)),
                "hinzh" => commands.push(Command::InjectOp(1, SemanticOperator::Hinzh)),
                "fuzen" => commands.push(Command::InjectOp(2, SemanticOperator::Fuzen)),
                "plika" => commands.push(Command::InjectOp(2, SemanticOperator::Plika)),
                "rezon" => commands.push(Command::InjectOp(3, SemanticOperator::Rezon)),
                "blum" => commands.push(Command::InjectOp(0, SemanticOperator::Blum)),
                "mokra" => commands.push(Command::InjectOp(1, SemanticOperator::Mokra)),
                "collapse" => commands.push(Command::InjectOp(0, SemanticOperator::Collapse)),
                "step" => commands.push(Command::Step(default_chronon)),
                "checkpoint" => commands.push(Command::Checkpoint),
                _ => {}
            }
        }

        // Push global semantic tokens into the dynamics engine pipeline
        if !active_phrase_tokens.is_empty() {
            commands.insert(0, Command::EvalTokens(active_phrase_tokens));
        }

        commands
    }
}