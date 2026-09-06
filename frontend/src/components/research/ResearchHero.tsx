import {
  APP_DESCRIPTION,
} from "@/lib/constants";


export function ResearchHero() {
  return (
    <div
      className="
        mx-auto
        max-w-3xl
        text-center
      "
    >
      <p
        className="
          mb-3
          text-sm
          font-semibold
          uppercase
          tracking-[0.14em]
          text-[var(--primary)]
        "
      >
        Multi-Agent Research
      </p>

      <h2
        id="research-title"
        className="
          text-3xl
          font-bold
          tracking-tight
          text-[var(--text-primary)]
          sm:text-4xl
          lg:text-5xl
        "
      >
        Research anything with
        multiple AI agents
      </h2>

      <p
        className="
          mx-auto
          mt-4
          max-w-2xl
          text-base
          text-[var(--text-secondary)]
          sm:text-lg
        "
      >
        {APP_DESCRIPTION}
      </p>
    </div>
  );
}