import { z } from 'zod';

export const VaultHeaderSchema = z.object({
  version: z.string().regex(/^\d+\.\d+\.\d+$/, "Version must be semantic versioning (x.y.z)").default("1.0.0"),
  createdAt: z.string().datetime().default(() => new Date().toISOString()),
  description: z.string().optional(),
});

export type VaultHeader = z.infer<typeof VaultHeaderSchema>;

export const VaultFileSchema = z.object({
  header: VaultHeaderSchema,
  secrets: z.record(z.string()),
});

export type VaultFile = z.infer<typeof VaultFileSchema>;

export interface LoadResult {
  totalVarsLoaded: number;
}
