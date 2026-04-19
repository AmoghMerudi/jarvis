import Chat from "@/components/Chat";
import Sidebar from "@/components/Sidebar";

export default function Home() {
  return (
    <div className="flex h-screen overflow-hidden" style={{ background: "var(--bg)" }}>
      <Sidebar />
      <main className="flex flex-col flex-1 min-w-0 border-l" style={{ borderColor: "var(--border)" }}>
        <Chat />
      </main>
    </div>
  );
}
