"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Bot } from "lucide-react";

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

    // use a unique slug every time
    const fullSlug = `${today}-${encodedTopicString}`;
    // Uncomment the next line if you want to add a random suffix for uniqueness
    // This is optional and can be used if you want to ensure the slug is always unique
    // This can be useful if you want to avoid collisions in case the same topics are submitted
    // but it will make the URL less readable.
    // const randomSuffix = Math.random().toString(36).substring(2, 6);
    // const fullSlug = `${today}-${encodedTopicString}-${randomSuffix}`;
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
            <a href="https://github.com/georgistan18/ServerlessAgent" target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-white">
              GitHub
            </a>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20">
    
        {/* Live Demo Section */}
        <section className="py-16 md:py-24">
          
          <Card className="bg-slate-800/90 border-slate-700 shadow-xl">
            <CardHeader className="text-center">
              <CardTitle className="text-3xl font-bold text-white">Company Analysis Generator Demo</CardTitle>
              <CardDescription className="text-slate-400 mt-2 text-md">
                Enter topics to generate an AI-powered company analysis using our multi-agent workflow.
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
                    placeholder="e.g., TotalSoft, Apple, Microsoft"
                    className="bg-slate-700 border-slate-600 placeholder-slate-500 text-white focus:ring-pink-500 focus:border-pink-500 h-12 text-lg"
                  />
                </div>
                <Button type="submit" className="w-full bg-pink-500 hover:bg-pink-600 text-lg py-3 h-auto">
                  <Bot className="mr-2 h-5 w-5" /> Generate company analysis
                </Button>
              </form>
            </CardContent>
            <CardFooter className="text-sm text-slate-500 px-6 sm:px-8 pt-6 text-center">
              <p>Watch how the agents research topics and format the results in real-time.</p>
            </CardFooter>
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
