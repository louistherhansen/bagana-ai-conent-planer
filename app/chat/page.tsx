import { ChatRuntimeProvider } from "@/components/ChatRuntimeProvider";
import { ChatInterface } from "@/components/ChatInterface";
import { PageLayout } from "@/components/PageLayout";

export default function ChatPage() {
  return (
    <ChatRuntimeProvider>
      <PageLayout currentPath="/chat">
        <ChatInterface />
      </PageLayout>
    </ChatRuntimeProvider>
  );
}
