/**
 * Path:
 * Removed the fixed height of the chat container.
 */
import AuthContext from "@/app/context/auth-context";
import { Loader2 } from "lucide-react";
import { useContext, useEffect, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import ChatActions from "./chat-actions";
import ChatMessage from "./chat-message";
import { ChatMode } from "./chat-mode";
import { ChatHandler } from "./chat.interface";

export default function ChatMessages(
  props: Pick<ChatHandler, "messages" | "isLoading" | "reload" | "stop">,
) {
  const scrollableChatContainerRef = useRef<HTMLDivElement>(null);
  const messageLength = props.messages.length;
  const lastMessage = props.messages[messageLength - 1];
  const authContext = useContext(AuthContext);

  const scrollToBottom = () => {
    if (scrollableChatContainerRef.current) {
      scrollableChatContainerRef.current.scrollTop =
        scrollableChatContainerRef.current.scrollHeight;
    }
  };

  const isLastMessageFromAssistant =
    messageLength > 0 && lastMessage?.role !== "user";
  const showReload =
    props.reload && !props.isLoading && isLastMessageFromAssistant;
  const showStop = props.stop && props.isLoading;

  // `isPending` indicate
  // that stream response is not yet received from the server,
  // so we show a loading indicator to give a better UX.
  const isPending = props.isLoading && !isLastMessageFromAssistant;

  useEffect(() => {
    scrollToBottom();
  }, [messageLength, lastMessage]);

  return (
    <div className="w-full h-full rounded-xl bg-white p-4 overflow-auto">
      {authContext && authContext.user && <ChatMode />}
      <div
        className="flex flex-col gap-5 divide-y pb-4"
        ref={scrollableChatContainerRef}
      >
        {props.messages.map((m) => (
          <ChatMessage
            key={m.id ? m.id : uuidv4()}
            chatMessage={m}
            isLoading={props.isLoading}
          />
        ))}
        {isPending && (
          <div className="flex justify-center items-center pt-10">
            <Loader2 className="h-4 w-4 animate-spin" />
          </div>
        )}
      </div>
      <div className="flex justify-end py-4">
        <ChatActions
          reload={props.reload}
          stop={props.stop}
          showReload={showReload}
          showStop={showStop}
        />
      </div>
    </div>
  );
}
