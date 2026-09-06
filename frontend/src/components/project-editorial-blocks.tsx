import type { PublicProjectEditorialBlock } from "@/lib/public-api";

import { ResponsiveImage } from "./responsive-image";

type ProjectEditorialBlocksProps = {
  blocks: PublicProjectEditorialBlock[];
};

export function ProjectEditorialBlocks({ blocks }: ProjectEditorialBlocksProps) {
  if (blocks.length === 0) return null;

  return (
    <section className="project-editorial-blocks section-shell">
      {blocks.map((block, index) => {
        if (block.block_type === "quote") {
          return (
            <blockquote className="project-editorial-blocks__quote" key={`${block.quote}-${index}`}>
              <p>“{block.quote}”</p>
              {block.attribution ? <footer>{block.attribution}</footer> : null}
            </blockquote>
          );
        }

        if (block.block_type === "text") {
          return (
            <article className="project-editorial-blocks__text" key={`${block.heading ?? "text"}-${index}`}>
              {block.heading ? <h2>{block.heading}</h2> : null}
              <p>{block.body}</p>
            </article>
          );
        }

        if (block.block_type === "paired_image") {
          return (
            <div className="project-editorial-blocks__pair" key={`pair-${index}`}>
              <ResponsiveImage image={block.left_image} sizes="(max-width: 767px) 100vw, 50vw" />
              <ResponsiveImage image={block.right_image} sizes="(max-width: 767px) 100vw, 50vw" />
            </div>
          );
        }

        if (block.block_type === "gallery") {
          return (
            <div className="project-editorial-blocks__gallery" key={`gallery-${index}`}>
              {block.images.map((image) => <ResponsiveImage image={image} key={image.url} sizes="(max-width: 767px) 100vw, 50vw" />)}
            </div>
          );
        }

        return (
          <div className={`project-editorial-blocks__image project-editorial-blocks__image--${block.block_type}`} key={`${block.block_type}-${index}`}>
            <ResponsiveImage image={block.image} sizes={block.block_type === "full_width_image" ? "100vw" : "(max-width: 767px) 100vw, 70vw"} />
          </div>
        );
      })}
    </section>
  );
}
