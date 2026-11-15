import type { MetadataRoute } from "next";
import { ORIGEM_SITE } from "@/lib/seo";
export default function robots(): MetadataRoute.Robots {
  // Permite ler noindex nos fluxos de conta; autorização permanece na API.
  return { rules: { userAgent: "*", allow: "/" }, sitemap: `${ORIGEM_SITE}/sitemap.xml` };
}
