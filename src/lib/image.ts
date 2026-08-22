import sharp from "sharp";

const THUMBNAIL_SIZE = 800;
const DETAIL_WIDTH = 1200;
const WEBP_QUALITY = 85;

export async function processThumbnail(input: Buffer): Promise<Buffer> {
  return sharp(input)
    .resize(THUMBNAIL_SIZE, THUMBNAIL_SIZE, { fit: "cover" })
    .webp({ quality: WEBP_QUALITY })
    .toBuffer();
}

export async function processDetailImage(input: Buffer): Promise<Buffer> {
  return sharp(input)
    .resize(DETAIL_WIDTH, null, { fit: "inside", withoutEnlargement: true })
    .webp({ quality: WEBP_QUALITY })
    .toBuffer();
}
