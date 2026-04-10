import Chat from "@/components/Chat";

export default function Home() {
  return (
    <main className="flex flex-col h-screen max-w-3xl mx-auto px-4">
      <header className="py-4 border-b border-gray-800">
        <h1 className="text-xl font-semibold">Jarvis</h1>
      </header>
      <Chat />
    </main>
  );
}
