# Codebase Explorer Prompt Template

Use this template when dispatching `codebase-explorer` agents. Launch 2-3 in parallel, each with a different mode.

## Mode 1: Architecture Mapping

> Map the architecture of the project: module structure, startup/initialisation flow, key abstractions, how components communicate. Report file paths for everything you read.

## Mode 2: Pattern Matching

> Find features similar to [FEATURE] in the project. Document coding conventions, file organization patterns, testing patterns, and UI/interface patterns. Report file paths.

## Mode 3: Integration Analysis

> Analyze where [FEATURE] would integrate into the project. What existing modules does it touch? What are the constraints? What dependencies exist? What could break? Report file paths.

## Usage

Replace `[FEATURE]` with the specific feature being planned or built. The main model reads key files the agents identify — don't rely solely on agent summaries.
