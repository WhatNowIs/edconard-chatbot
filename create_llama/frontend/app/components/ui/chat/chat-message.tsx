import { Check, Copy } from "lucide-react";

import AuthContext from "@/app/context/auth-context";
import { Message } from "ai";
import { Fragment, useContext } from "react";
import { Button } from "../button";
import ChatAvatar from "./chat-avatar";
import { ChatEvents } from "./chat-events";
import { ChatImage } from "./chat-image";
import { ChatSources } from "./chat-sources";
import ChatTools from "./chat-tools";
import {
  AnnotationData,
  EventData,
  ImageData,
  MessageAnnotation,
  MessageAnnotationType,
  SourceData,
  ToolData,
} from "./index";
import Markdown from "./markdown";
import { useCopyToClipboard } from "./use-copy-to-clipboard";

type ContentDisplayConfig = {
  order: number;
  component: JSX.Element | null;
};

function getAnnotationData<T extends AnnotationData>(
  annotations: MessageAnnotation[],
  type: MessageAnnotationType,
): T[] {
  return annotations.filter((a) => a.type === type).map((a) => a.data as T);
}

function ChatMessageContent({
  message,
  isLoading,
}: {
  message: Message;
  isLoading: boolean;
}) {
  const authContext = useContext(AuthContext);
  const annotations = message.annotations as MessageAnnotation[] | undefined;

  const source =
    message.role === "assistant" &&
    !authContext?.isResearchExploration &&
    message.annotations &&
    message.annotations[0] &&
    (message?.annotations[0] as any)?.headline !== undefined
      ? `Editorial Template: ${(message.annotations[0] as any)?.url}\nHeadline: ${(message.annotations[0] as any)?.headline}\nOrder of Appearance: ${(message.annotations[0] as any)?.order}\n\n`
      : "";

  if (!annotations?.length && authContext?.isResearchExploration)
    return (
      <Markdown
        content={message.content}
        role={message.role}
        annotations={message.annotations as any[]}
      />
    );

  if (authContext?.isResearchExploration) {
    const imageData = getAnnotationData<ImageData>(
      annotations as MessageAnnotation[],
      MessageAnnotationType.IMAGE,
    );
    const eventData = getAnnotationData<EventData>(
      annotations as MessageAnnotation[],
      MessageAnnotationType.EVENTS,
    );
    const sourceData = getAnnotationData<SourceData>(
      annotations as MessageAnnotation[],
      MessageAnnotationType.SOURCES,
    );
    const toolData = getAnnotationData<ToolData>(
      annotations as MessageAnnotation[],
      MessageAnnotationType.TOOLS,
    );

    const contents: ContentDisplayConfig[] = [
      {
        order: -3,
        component: imageData[0] ? <ChatImage data={imageData[0]} /> : null,
      },
      {
        order: -2,
        component:
          eventData.length > 0 ? (
            <ChatEvents
              isLoading={isLoading}
              data={eventData}
              citations={sourceData[0] ? sourceData[0].nodes : []}
            />
          ) : null,
      },
      {
        order: -1,
        component: toolData[0] ? <ChatTools data={toolData[0]} /> : null,
      },
      {
        order: 0,
        component: (
          <Markdown
            content={source + message.content}
            annotations={message.annotations as any[]}
            role={message.role}
          />
        ),
      },
      {
        order: 1,
        component: sourceData[0] ? <ChatSources data={sourceData[0]} /> : null,
      },
    ];
    return (
      <div className="flex-1 gap-4 flex flex-col">
        {contents
          .sort((a, b) => a.order - b.order)
          .map((content, index) => (
            <Fragment key={index}>{content.component}</Fragment>
          ))}
      </div>
    );
  }
  const contents: ContentDisplayConfig[] = [
    {
      order: 0,
      component: (
        <Markdown
          content={source + message.content}
          annotations={message.annotations as any[]}
          role={message.role}
        />
      ),
    },
  ];

  return (
    <div className="flex-1 gap-4 flex flex-col">
      {contents
        .sort((a, b) => a.order - b.order)
        .map((content, index) => (
          <Fragment key={index}>{content.component}</Fragment>
        ))}
    </div>
  );
}

export default function ChatMessage({
  chatMessage,
  isLoading,
}: {
  chatMessage: Message;
  isLoading: boolean;
}) {
  const { isCopied, copyToClipboard } = useCopyToClipboard({ timeout: 2000 });
  return (
    <div className="flex items-start gap-4 pr-5 pt-5">
      <ChatAvatar role={chatMessage.role} />
      <div className="group flex flex-1 justify-between gap-2">
        <ChatMessageContent message={chatMessage} isLoading={isLoading} />
        <Button
          onClick={() => copyToClipboard(chatMessage.content)}
          size="icon"
          variant="ghost"
          className="h-8 w-8 opacity-0 group-hover:opacity-100"
        >
          {isCopied ? (
            <Check className="h-4 w-4" />
          ) : (
            <Copy className="h-4 w-4" />
          )}
        </Button>
      </div>
    </div>
  );
}
