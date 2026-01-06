import { GoogleGenerativeAI } from "@google/generative-ai";

export class LLMService {
    private genAI: GoogleGenerativeAI;
    private model: any;

    constructor(apiKey: string) {
        this.genAI = new GoogleGenerativeAI(apiKey);
        this.model = this.genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
    }

    async generateInsights(productData: string): Promise<string> {
        const prompt = `
      Analyze the following product data and provide key insights, 
      potential selling points, and areas for improvement.
      
      Product Data:
      ${productData}
    `;

        try {
            const result = await this.model.generateContent(prompt);
            const response = await result.response;
            return response.text();
        } catch (error) {
            console.error("Gemini API Error:", error);
            throw new Error("Failed to communicate with LLM provider.");
        }
    }
}
