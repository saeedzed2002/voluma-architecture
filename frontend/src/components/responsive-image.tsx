import type { PublicImage } from "@/lib/public-api";

type ResponsiveImageProps = {
  alt?: string;
  className?: string;
  fill?: boolean;
  image: PublicImage;
  loading?: "eager" | "lazy";
  priority?: boolean;
  sizes: string;
};

export function ResponsiveImage({
  alt,
  className,
  fill = false,
  image,
  loading = "lazy",
  priority = false,
  sizes,
}: ResponsiveImageProps) {
  return (
    <picture className={fill ? "responsive-image responsive-image--fill" : "responsive-image"}>
      {image.avif_srcset ? <source sizes={sizes} srcSet={image.avif_srcset} type="image/avif" /> : null}
      {image.webp_srcset ? <source sizes={sizes} srcSet={image.webp_srcset} type="image/webp" /> : null}
      <img
        alt={alt ?? image.alt}
        className={className}
        decoding="async"
        fetchPriority={priority ? "high" : "auto"}
        height={image.height ?? undefined}
        loading={loading}
        sizes={sizes}
        src={image.url}
        width={image.width ?? undefined}
      />
    </picture>
  );
}
