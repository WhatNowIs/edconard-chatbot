/* eslint-disable @typescript-eslint/no-explicit-any */
import "katex/dist/katex.min.css";
import { FC, memo, useContext } from "react";
import ReactMarkdown, { Options } from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";

import AuthContext from "@/app/context/auth-context";
import { CodeBlock } from "./codeblock";

const MemoizedReactMarkdown: FC<Options> = memo(
  ReactMarkdown,
  (prevProps, nextProps) =>
    prevProps.children === nextProps.children &&
    prevProps.className === nextProps.className,
);

const preprocessLaTeX = (content: string) => {
  // Replace block-level LaTeX delimiters \[ \] with $$ $$
  const blockProcessedContent = content.replace(
    /\\\[(.*?)\\\]/gs,
    (_, equation) => `$$${equation}$$`,
  );
  // Replace inline LaTeX delimiters \( \) with $ $
  const inlineProcessedContent = blockProcessedContent.replace(
    /\\\((.*?)\\\)/gs,
    (_, equation) => `$${equation}$`,
  );
  return inlineProcessedContent;
};

export default function Markdown({
  content,
  annotations,
  role,
}: {
  content: string;
  role: string;
  annotations: any[];
}) {
  const authContext = useContext(AuthContext);
  const processedContent = preprocessLaTeX(content);
  return (
    <MemoizedReactMarkdown
      className="prose dark:prose-invert prose-p:leading-relaxed prose-pre:p-0 break-words custom-markdown"
      remarkPlugins={[remarkGfm, remarkMath]}
      rehypePlugins={[rehypeKatex as unknown as any]}
      components={{
        p({ children }) {
          let result =
            role === "assistant" &&
            annotations[0] &&
            annotations[0]?.headline !== undefined
              ? `{${annotations[0]?.headline}}, Article Order of Appearance - ${annotations[0]?.order}: ${annotations[0]?.url}\n\n`
              : "";
          return (
            <p className="mb-2 last:mb-0 whitespace-pre-line">{`${role === "assistant" && !authContext?.isResearchExploration ? result : ""}${children}`}</p>
          );
        },
        code({ inline, className, children, ...props }) {
          if (children.length) {
            if (children[0] == "▍") {
              return (
                <span className="mt-1 animate-pulse cursor-default whitespace-pre-line">
                  ▍
                </span>
              );
            }

            children[0] = (children[0] as string).replace("`▍`", "▍");
          }

          const match = /language-(\w+)/.exec(className || "");

          if (inline) {
            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          }

          return (
            <CodeBlock
              key={Math.random()}
              language={(match && match[1]) || ""}
              value={String(children).replace(/\n$/, "")}
              {...props}
            />
          );
        },
      }}
    >
      {processedContent}
    </MemoizedReactMarkdown>
  );
}
