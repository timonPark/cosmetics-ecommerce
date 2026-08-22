import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { processThumbnail, processDetailImage } from "@/lib/image";

const r2 = new S3Client({
  region: "auto",
  endpoint: `https://${process.env.R2_ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: {
    accessKeyId: process.env.R2_ACCESS_KEY_ID!,
    secretAccessKey: process.env.R2_SECRET_ACCESS_KEY!,
  },
});

async function uploadToR2(key: string, buffer: Buffer): Promise<string> {
  await r2.send(
    new PutObjectCommand({
      Bucket: process.env.R2_BUCKET_NAME!,
      Key: key,
      Body: buffer,
      ContentType: "image/webp",
    })
  );
  return `${process.env.R2_PUBLIC_URL}/${key}`;
}

export async function uploadThumbnail(slug: string, input: Buffer): Promise<string> {
  const buffer = await processThumbnail(input);
  return uploadToR2(`products/${slug}/thumbnail.webp`, buffer);
}

export async function uploadDetailImage(slug: string, input: Buffer): Promise<string> {
  const buffer = await processDetailImage(input);
  return uploadToR2(`products/${slug}/detail.webp`, buffer);
}
