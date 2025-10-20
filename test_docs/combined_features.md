---
tags: feature_complete, status_testing, theme_comprehensive
categories: test_all_features
---

# Combined Features Test

This note combines multiple features to ensure they work together.

## Wiki Links in Callouts

> [!note] Navigation
> See [[basic_test|Basic Example]] for simple formatting.
> Check out [[callouts_test]] for callout examples.
> Review [[labels_test|Label Testing]] for metadata.

## Callouts with Code and Links

> [!tip] Code Example
> Here's how to use wiki links:
> ```markdown
> [[note_name|Display Text]]
> [[parent/note_name|Text]]
> ```
>
> Read more in [[wiki_links_test]].

## Multiple Callout Types

> [!important]
> Important information with [[basic_test]] reference.

> [!warning] Watch Out
> This references [[non_existent_placeholder]] which will create a placeholder.

## Complex Content

### Tables

| Feature | Status | Link |
|---------|--------|------|
| Labels | ✅ | [[labels_test]] |
| Wiki Links | ✅ | [[wiki_links_test]] |
| Callouts | ✅ | [[callouts_test]] |

### Task List

- [x] Basic Markdown
- [x] Frontmatter labels
- [x] Wiki links
- [x] Callouts
- [ ] Advanced features

## Nested Formatting

> [!example] Complex Example
> This callout contains:
>
> 1. **Bold text** and *italic text*
> 2. A link to [[basic_test|the basic test]]
> 3. `inline code`
> 4. Multiple paragraphs
>
> And it references [[labels_test]] as well.

## Path-Based Wiki Links

Testing path syntax:
- [[Examples/Tutorial/Getting Started|Getting Started Guide]]
- [[Reference/API Documentation|API Docs]]
- Simple link: [[callouts_test]]
