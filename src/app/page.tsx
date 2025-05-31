"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Newspaper, Bot, Lightbulb, Search } from "lucide-react";

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
            <h1 className="text-2xl font-bold">Serverless Agents</h1>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20">
        <section className="grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <h2 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight">
              AI-Powered Newsletters,
              <br />
              <span className="text-pink-400">Effortlessly Generated.</span>
            </h2>
            <p className="text-lg sm:text-xl text-slate-400 max-w-xl">
              Leverage the power of AI to create insightful newsletters on any topic.
              Our serverless agents search the web for the latest information and deliver
              concise summaries directly to you.
            </p>
          </div>
          <div className="hidden md:block relative aspect-video bg-slate-800 rounded-xl shadow-2xl overflow-hidden">
            {/* Placeholder for an animation or a relevant graphic */}
            <div className="absolute inset-0 flex items-center justify-center">
              <Newspaper className="h-32 w-32 text-pink-500 opacity-30 animate-pulse" />
            </div>
             <div className="absolute top-1/4 left-1/4 w-24 h-24 bg-pink-500/20 rounded-full filter blur-2xl animate-blob animation-delay-2000"></div>
            <div className="absolute top-1/2 right-1/4 w-32 h-32 bg-indigo-500/20 rounded-full filter blur-2xl animate-blob animation-delay-4000"></div>
          </div>
        </section>

        {/* Newsletter Generation Section */}
        <section className="py-16 md:py-24">
          <Card className="bg-slate-800/90 border-slate-700 shadow-xl">
            <CardHeader className="text-center">
              <CardTitle className="text-3xl font-bold text-white">Create Your Newsletter</CardTitle>
              <CardDescription className="text-slate-400 mt-2 text-md">
                Enter a few topics, and let our AI agent craft a newsletter for you.
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
              <p>Our AI will search for the latest information and compile a summary.</p>
            </CardFooter>
          </Card>
        </section>

        {/* Features Section (Example) */}
        <section className="py-16 md:py-24 text-center">
           <h3 className="text-3xl font-bold mb-4">Why Choose Serverless Agents?</h3>
           <p className="text-slate-400 mb-12 max-w-2xl mx-auto">
            Our platform offers a unique blend of power, simplicity, and cutting-edge AI to keep you informed.
           </p>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="flex flex-col items-center p-6 bg-slate-800/50 rounded-lg border border-slate-700/50">
              <Search className="h-12 w-12 text-pink-400 mb-4" />
              <h4 className="text-xl font-semibold mb-2">Always Up-to-Date</h4>
              <p className="text-slate-400 text-sm">Agents fetch the latest information from the web.</p>
            </div>
            <div className="flex flex-col items-center p-6 bg-slate-800/50 rounded-lg border border-slate-700/50">
              <Bot className="h-12 w-12 text-pink-400 mb-4" />
              <h4 className="text-xl font-semibold mb-2">AI-Powered Summaries</h4>
              <p className="text-slate-400 text-sm">Concise and relevant content generated by AI.</p>
            </div>
            <div className="flex flex-col items-center p-6 bg-slate-800/50 rounded-lg border border-slate-700/50">
              <Lightbulb className="h-12 w-12 text-pink-400 mb-4" />
              <h4 className="text-xl font-semibold mb-2">Simple & Scalable</h4>
              <p className="text-slate-400 text-sm">Easy to use and built on serverless architecture.</p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="py-8 text-center border-t border-slate-700/50">
        <p className="text-slate-500">&copy; {new Date().getFullYear()} Serverless Agents. All rights reserved.</p>
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
