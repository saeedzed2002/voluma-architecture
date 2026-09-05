type EditorialHeaderProps = {
  eyebrow: string;
  intro: string;
  title: string;
};

export function EditorialHeader({ eyebrow, intro, title }: EditorialHeaderProps) {
  return (
    <header className="editorial-page__header">
      <p>{eyebrow}</p>
      <h1>{title}</h1>
      <p>{intro}</p>
    </header>
  );
}
