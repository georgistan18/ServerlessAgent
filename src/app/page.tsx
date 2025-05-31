"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Bot, Code, Zap, Server } from "lucide-react";

export default function HomePage() {
  const [topics, setTopics] = useState('');
  const router = useRouter();

  const handleTopicChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setTopics(event.target.value);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedTopics = topics.trim();
    if (trimmedTopics === '') {
      // Optionally, show an error message if topics are empty
      return;
    }
    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    
    // Split topics by comma, then encode each one individually
    const individualTopics = trimmedTopics.split(',').map(topic => topic.trim()).filter(topic => topic !== '');
    const encodedTopicString = individualTopics.map(topic => topic.replace(/ /g, '+')).join('~');

    const fullSlug = `${today}-${encodedTopicString}`;
    router.push(`/newsletter/${fullSlug}`);
  };

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-slate-950 to-slate-800 text-white">
      {/* Header */}
      <header className="container mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bot className="h-8 w-8 text-pink-400" />
            <h1 className="text-2xl font-bold">Serverless Agent Architecture</h1>
          </div>
          <div className="flex items-center space-x-4">
            <a href="https://github.com/brookr/serverless-agents" target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-white">
              GitHub
            </a>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20">
        <section className="grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <h2 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight">
              Build AI Apps with
              <br />
              <span className="text-pink-400">Serverless Agents</span>
            </h2>
            <p className="text-lg sm:text-xl text-slate-400 max-w-xl">
              A production-ready starter for building scalable AI applications with Python agents on Vercel, 
              orchestrated by Inngest, and powered by Next.js. Deploy AI workflows that scale automatically.
            </p>
            <div className="flex flex-wrap gap-4">
              <a href="https://github.com/brookr/serverless-agents" target="_blank" rel="noopener noreferrer">
                <Button variant="outline" className="border-slate-600 text-slate-800 hover:text-slate-900 hover:bg-slate-200">
                  <Code className="mr-2 h-4 w-4" />
                  View on GitHub
                </Button>
              </a>
              <a href="https://github.com/brookr/serverless-agents#readme" target="_blank" rel="noopener noreferrer">
                <Button variant="outline" className="border-slate-600 text-slate-800 hover:text-slate-900 hover:bg-slate-200">
                  📚 Read the Docs
                </Button>
              </a>
            </div>
          </div>
          <div className="hidden md:block relative aspect-video bg-slate-800 rounded-xl shadow-2xl overflow-hidden">
            {/* Architecture visualization */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="grid grid-cols-2 gap-4 p-8">
                <div className="flex flex-col items-center">
                  <Bot className="h-12 w-12 text-pink-400 mb-2" />
                  <span className="text-xs text-slate-400">AI Agents</span>
                </div>
                <div className="flex flex-col items-center">
                  <Server className="h-12 w-12 text-indigo-400 mb-2" />
                  <span className="text-xs text-slate-400">Inngest</span>
                </div>
                <div className="flex flex-col items-center">
                  <Zap className="h-12 w-12 text-yellow-400 mb-2" />
                  <span className="text-xs text-slate-400">Vercel</span>
                </div>
                <div className="flex flex-col items-center">
                  <Code className="h-12 w-12 text-blue-400 mb-2" />
                  <span className="text-xs text-slate-400">Next.js</span>
                </div>
              </div>
            </div>
            <div className="absolute top-1/4 left-1/4 w-24 h-24 bg-pink-500/20 rounded-full filter blur-2xl animate-blob animation-delay-2000"></div>
            <div className="absolute top-1/2 right-1/4 w-32 h-32 bg-indigo-500/20 rounded-full filter blur-2xl animate-blob animation-delay-4000"></div>
          </div>
        </section>

        {/* Live Demo Section */}
        <section className="py-16 md:py-24">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold mb-4">Try the Live Demo</h3>
            <p className="text-slate-400 max-w-2xl mx-auto">
              This starter includes a newsletter generator as an example implementation. 
              Try it out to see the serverless agent architecture in action.
            </p>
          </div>
          <Card className="bg-slate-800/90 border-slate-700 shadow-xl">
            <CardHeader className="text-center">
              <CardTitle className="text-3xl font-bold text-white">Newsletter Generator Demo</CardTitle>
              <CardDescription className="text-slate-400 mt-2 text-md">
                Enter topics to generate an AI-powered newsletter using our multi-agent workflow.
              </CardDescription>
            </CardHeader>
            <CardContent className="px-6 sm:px-8">
              <form className="space-y-6" onSubmit={handleSubmit}>
                <div>
                  <label htmlFor="topicsInput" className="block text-sm font-medium text-slate-300 mb-2">
                    Topics (comma-separated)
                  </label>
                  <Input
                    id="topicsInput"
                    name="topics"
                    type="text"
                    value={topics}
                    onChange={handleTopicChange}
                    placeholder="e.g., Artificial Intelligence, Climate Tech, Quantum Computing"
                    className="bg-slate-700 border-slate-600 placeholder-slate-500 text-white focus:ring-pink-500 focus:border-pink-500 h-12 text-lg"
                  />
                </div>
                <Button type="submit" className="w-full bg-pink-500 hover:bg-pink-600 text-lg py-3 h-auto">
                  <Bot className="mr-2 h-5 w-5" /> Generate Newsletter
                </Button>
              </form>
            </CardContent>
            <CardFooter className="text-sm text-slate-500 px-6 sm:px-8 pt-6 text-center">
              <p>Watch how the agents research topics and format the results in real-time.</p>
            </CardFooter>
          </Card>
        </section>

        {/* Architecture Features Section */}
        <section className="py-16 md:py-24 text-center">
          <h3 className="text-3xl font-bold mb-4">Built for Modern AI Applications</h3>
          <p className="text-slate-400 mb-12 max-w-2xl mx-auto">
            This starter provides everything you need to build production-ready AI applications with serverless architecture.
          </p>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="flex flex-col items-center p-6 bg-slate-800/50 rounded-lg border border-slate-700/50">
              <Server className="h-12 w-12 text-pink-400 mb-4" />
              <h4 className="text-xl font-semibold mb-2">Serverless Agents</h4>
              <p className="text-slate-400 text-sm">Python FastAPI agents deploy automatically to Vercel Functions.</p>
            </div>
            <div className="flex flex-col items-center p-6 bg-slate-800/50 rounded-lg border border-slate-700/50">
              <Zap className="h-12 w-12 text-pink-400 mb-4" />
              <h4 className="text-xl font-semibold mb-2">Long-Running Workflows</h4>
              <p className="text-slate-400 text-sm">Inngest handles complex workflows that exceed typical timeouts.</p>
            </div>
            <div className="flex flex-col items-center p-6 bg-slate-800/50 rounded-lg border border-slate-700/50">
              <Code className="h-12 w-12 text-pink-400 mb-4" />
              <h4 className="text-xl font-semibold mb-2">Full-Stack TypeScript</h4>
              <p className="text-slate-400 text-sm">Type-safe from frontend to backend with Next.js App Router.</p>
            </div>
          </div>
        </section>

        {/* Get Started Section */}
        <section className="py-16 md:py-24">
          <Card className="bg-gradient-to-r from-pink-500/10 to-indigo-500/10 border-slate-700">
            <CardContent className="p-8 text-center">
              <h3 className="text-2xl font-bold mb-4 text-white">Ready to Build?</h3>
              <p className="text-slate-400 mb-6 max-w-xl mx-auto">
                Clone this repository and start building your own AI-powered application with our serverless architecture.
              </p>
              <div className="flex flex-wrap gap-4 justify-center">
                <a href="https://github.com/brookr/serverless-agents" target="_blank" rel="noopener noreferrer">
                  <Button className="bg-pink-500 hover:bg-pink-600">
                    Get Started →
                  </Button>
                </a>
              </div>
            </CardContent>
          </Card>
        </section>
      </main>

      {/* Footer */}
      <footer className="py-8 text-center border-t border-slate-700/50">
        <p className="text-slate-500">Released under CC0 License • Build amazing AI applications</p>
      </footer>
    </div>
  );
}

// Add some simple CSS animations for the blobs in globals.css if you want them to move
// For example, in src/app/globals.css:
/*
@keyframes blob {
  0% {
    transform: scale(1) translate(0, 0);
  }
  33% {
    transform: scale(1.1) translate(20px, -30px);
  }
  66% {
    transform: scale(0.9) translate(-20px, 20px);
  }
  100% {
    transform: scale(1) translate(0, 0);
  }
}

.animate-blob {
  animation: blob 15s infinite cubic-bezier(0.68, -0.55, 0.27, 1.55);
}
.animation-delay-2000 {
  animation-delay: 2s;
}
.animation-delay-4000 {
  animation-delay: 4s;
}
*/
