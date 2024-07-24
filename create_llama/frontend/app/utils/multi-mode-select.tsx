import { z } from "zod";

export const ArticleSchema = z.object({
  headline: z.string(),
  publisher: z.string(),
  authors: z.string(),
  abstract: z.string(),
  question: z.string(),
});

export type Article = z.infer<typeof ArticleSchema>;

export function extractArticleDataFromString(
  inputString: string,
): Article | null {
  const pattern = /(\w+)={(.*?)}/g;
  let match;
  const result: { [key: string]: string } = {};

  while ((match = pattern.exec(inputString)) !== null) {
    const [, key, value] = match;
    result[key] = value;
  }

  try {
    return ArticleSchema.parse(result);
  } catch (e) {
    return null;
  }
}

export function convertArticleToString(article: Article): string {
  return `headline={${article.headline}};publisher={${article.publisher}};authors={${article.authors}};abstract={${article.abstract}}`;
}

export enum SupportedChatModeEnum {
  ResearchOrExploration = "research-or-exploration",
  MacroRoundupArticleTweetGeneration = "macro-roundup-article-tweet-generation",
  MacroRoundupArticleSEOTitleAndMetaDescriptionGeneration = "macro-roundup-article-seo-title-and-meta-description-generation",
  MacroRoundupArticleTopicGeneration = "macro-roundup-article-topic-generation",
  MacroRoundupArticleSummaryOptimization = "macro-roundup-article-summary-optimization",
}

export const supportedChatMode = [
  {
    name: "Research/Exploration",
    value: "research-or-exploration",
  },
  {
    name: "Macro Roundup Article Tweet Generation",
    value: "macro-roundup-article-tweet-generation",
  },
  {
    name: "Macro Roundup Article SEO Title and Meta Description Generation",
    value: "macro-roundup-article-seo-title-and-meta-description-generation",
  },
  {
    name: "Macro Roundup Article Topic Generation",
    value: "macro-roundup-article-topic-generation",
  },
  {
    name: "Macro Roundup Article Summary Optimization",
    value: "macro-roundup-article-summary-optimization",
  },
];
