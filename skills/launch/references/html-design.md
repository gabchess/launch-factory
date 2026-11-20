# HTML design and copy

Use this shared contract for the launch map and captioned explainer. Keep the supplied standalone templates; fill their JSON rather than adding a framework, remote asset or custom renderer.

- Write clear, complete sentences that a 12-year-old can follow. Use familiar words without slang. Keep important technical terms and explain them briefly when needed. Do not remove a limit or caveat to make a label shorter.
- Include a useful flowchart. Name what its arrows mean: supported product steps, the order of the story, or explicitly proposed next actions. Story order does not prove causality. Never invent a product sequence or a result to fill a diagram. The map contract defines its flow fields; the explainer derives its story flow from its scene headlines.
- Use Proxima Nova if it is available on the viewer's device. The templates use a readable system sans fallback. They contain no font files and make no font request. Do not buy, install or redistribute a font as part of drafting, and do not claim Proxima rendered without checking it.
- Keep the black-to-blue background gradient in both templates, regardless of the device's light/dark setting. High-contrast foreground panels protect text over the gradient. Graphics, arrows and active-step markers should explain the content, not decorate it.
- End the visual with a short, source-backed summary, before the source appendix. The map uses its summary list; the explainer shows its existing takeaways below the playback controls. Keep the script matched to the scene and end-card captions; the summary adds no narration.
- Reflow on narrow screens. Do not shrink labels until they fit. Aim for at least 18 px main labels and 16 px supporting text, meaningful heading order and information that is available without hover or motion.

When browser tools are available, inspect the actual file around 1280 px and 390 px wide. Check wrapping, horizontal overflow, arrows, text/background contrast and keyboard operation. For the explainer, check first scene, an exact scene boundary, pause/replay and the closing summary. State the actual tool, file and widths with a visual-verification claim. If opening or inspection is unavailable, say so; source checks alone do not prove the rendering.

Keep all spec text in plain text nodes. Preserve JSON `<` escaping, source-number validation, visible Sources and Not traced lists, and the explainer's time-based `renderAt` behavior. A chart is still a draft: it does not prove availability, customer results, publication, rendered video or audio.
