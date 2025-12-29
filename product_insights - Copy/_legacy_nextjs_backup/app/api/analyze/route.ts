import { NextRequest, NextResponse } from "next/server";
import { LLMService } from "@/lib/llm-service";

export async function POST(req: NextRequest) {
    try {
        const apiKey = process.env.GEMINI_API_KEY;
        if (!apiKey) {
            return NextResponse.json(
                { error: "Server Configuration Error: Missing API Key" },
                { status: 500 }
            );
        }

        const body = await req.json();
        const { productData } = body;

        if (!productData) {
            return NextResponse.json(
                { error: "Missing product data" },
                { status: 400 }
            );
        }

        const llm = new LLMService(apiKey);
        const insights = await llm.generateInsights(productData);

        return NextResponse.json({ insights });
    } catch (error) {
        console.error("Analysis Error:", error);
        return NextResponse.json(
            { error: "Failed to generate insights" },
            { status: 500 }
        );
    }
}
