import type { PublicProjectEditorialBlock } from "@/lib/public-api";

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

        return (
          <article className="project-editorial-blocks__text" key={`${block.heading ?? "text"}-${index}`}>
            {block.heading ? <h2>{block.heading}</h2> : null}
            <p>{block.body}</p>
          </article>
        );
      })}
    </section>
  );
}
