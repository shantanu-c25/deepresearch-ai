import {
  render,
  screen,
} from "@testing-library/react";

import {
  describe,
  expect,
  it,
} from "vitest";

import {
  MarkdownRenderer,
} from "./MarkdownRenderer";


describe("MarkdownRenderer", () => {
  it(
    "renders Markdown as semantic HTML",
    () => {
      const markdown = `
# Research Summary

This is **important research**.

## Key Findings

- Finding one
- Finding two

[OpenAI](https://openai.com)
`;

      render(
        <MarkdownRenderer
          content={markdown}
        />
      );

      expect(
        screen.getByRole(
          "heading",
          {
            name:
              "Research Summary",
          }
        )
      ).toBeInTheDocument();

      expect(
        screen.getByRole(
          "heading",
          {
            name:
              "Key Findings",
          }
        )
      ).toBeInTheDocument();

      expect(
        screen.getByText(
          "important research"
        ).tagName
      ).toBe("STRONG");

      expect(
        screen.getByText(
          "Finding one"
        )
      ).toBeInTheDocument();

      expect(
        screen.getByRole(
          "link",
          {
            name:
              /OpenAI/i,
          }
        )
      ).toHaveAttribute(
        "href",
        "https://openai.com"
      );
    }
  );
});