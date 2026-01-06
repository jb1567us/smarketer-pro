"use client";

import { useState } from "react";
import { Send, Sparkles } from "lucide-react";

export default function Home() {
    const [input, setInput] = useState("");
    const [result, setResult] = useState("");
    const [loading, setLoading] = useState(false);

    const handleAnalyze = async () => {
        if (!input.trim()) return;
        setLoading(true);
        setResult("");

        try {
            const res = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ productData: input }),
            });

            const data = await res.json();
            if (data.error) throw new Error(data.error);

            setResult(data.insights);
        } catch (e) {
            setResult("Error: Failed to fetch insights. Please check API Key configuration.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="flex min-h-screen flex-col items-center p-8 md:p-24 bg-gray-50 dark:bg-zinc-900">
            <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex mb-10">
                <p className="fixed left-0 top-0 flex w-full justify-center border-b border-gray-300 bg-white pb-6 pt-8 backdrop-blur-2xl dark:border-neutral-800 dark:bg-zinc-800/30 lg:static lg:w-auto lg:rounded-xl lg:border lg:bg-gray-200 lg:p-4 lg:dark:bg-zinc-800/30">
                    Product Insights Analysis
                </p>
            </div>

            <div className="relative flex place-items-center mb-10">
                <h1 className="text-4xl md:text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-cyan-500 pb-2">
                    Unlock Product Potential
                </h1>
            </div>

            <div className="w-full max-w-2xl grid gap-6">
                <div className="bg-white dark:bg-zinc-800 p-6 rounded-2xl shadow-xl border border-gray-100 dark:border-zinc-700">
                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                        Product Description / Data
                    </label>
                    <textarea
                        className="w-full h-40 p-4 rounded-xl border border-gray-200 dark:border-zinc-600 bg-gray-50 dark:bg-zinc-900 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                        placeholder="Paste your product details here..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                    />
                    <button
                        onClick={handleAnalyze}
                        disabled={loading}
                        className="mt-4 w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <span className="animate-pulse">Analyzing...</span>
                        ) : (
                            <>
                                <Sparkles className="w-5 h-5" /> Generate Insights
                            </>
                        )}
                    </button>
                </div>

                {result && (
                    <div className="bg-white dark:bg-zinc-800 p-8 rounded-2xl shadow-xl border border-blue-100 dark:border-blue-900/30 animation-fade-in">
                        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2 text-blue-600">
                            <Sparkles className="w-5 h-5" /> AI Analysis
                        </h3>
                        <div className="prose dark:prose-invert max-w-none whitespace-pre-wrap">
                            {result}
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}
