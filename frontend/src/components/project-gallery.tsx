"use client";

import Image from "next/image";
import { useRef, useState } from "react";

import type { Locale } from "@/i18n/routing";

import { ArrowIcon, CloseIcon } from "./icons";

export type GalleryImage = {
  src: string;
  alt: string;
  caption: string;
};

type ProjectGalleryProps = {
  closeLabel: string;
  images: GalleryImage[];
  locale: Locale;
  nextLabel: string;
  openLabel: string;
  previousLabel: string;
};

export function ProjectGallery({
  closeLabel,
  images,
  locale,
  nextLabel,
  openLabel,
  previousLabel,
}: ProjectGalleryProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const returnFocusRef = useRef<HTMLButtonElement | null>(null);
  const [activeIndex, setActiveIndex] = useState(0);

  const openImage = (index: number, trigger: HTMLButtonElement) => {
    setActiveIndex(index);
    returnFocusRef.current = trigger;
    dialogRef.current?.showModal();
  };

  const closeDialog = () => dialogRef.current?.close();

  const moveImage = (offset: number) => {
    setActiveIndex((current) => (current + offset + images.length) % images.length);
  };

  return (
    <>
      <div className="project-gallery">
        {images.map((image, index) => (
          <figure className="project-gallery__figure" key={`${image.src}-${image.caption}`}>
            <button
              aria-label={`${openLabel}: ${image.caption}`}
              className="project-gallery__button"
              onClick={(event) => openImage(index, event.currentTarget)}
              type="button"
            >
              <Image alt={image.alt} fill sizes="(max-width: 767px) 100vw, 50vw" src={image.src} />
            </button>
            <figcaption>{image.caption}</figcaption>
          </figure>
        ))}
      </div>

      <dialog
        aria-label={images[activeIndex].caption}
        className="gallery-dialog"
        onClick={(event) => {
          if (event.target === dialogRef.current) closeDialog();
        }}
        onClose={() => returnFocusRef.current?.focus()}
        onKeyDown={(event) => {
          if (event.key === "ArrowLeft") {
            event.preventDefault();
            moveImage(-1);
          }
          if (event.key === "ArrowRight") {
            event.preventDefault();
            moveImage(1);
          }
        }}
        ref={dialogRef}
      >
        <button
          aria-label={closeLabel}
          className="gallery-dialog__close"
          onClick={closeDialog}
          type="button"
        >
          <CloseIcon className="control-icon" />
        </button>
        <div className="gallery-dialog__controls">
          <button
            aria-label={previousLabel}
            className="gallery-dialog__previous"
            onClick={() => moveImage(-1)}
            type="button"
          >
            <ArrowIcon className="directional-icon directional-icon--back" />
          </button>
          <p aria-live="polite">
            {locale === "fa"
              ? `تصویر ${activeIndex + 1} از ${images.length}`
              : `Image ${activeIndex + 1} of ${images.length}`}
          </p>
          <button
            aria-label={nextLabel}
            className="gallery-dialog__next"
            onClick={() => moveImage(1)}
            type="button"
          >
            <ArrowIcon className="directional-icon" />
          </button>
        </div>
        <figure>
          <div className="gallery-dialog__media">
            <Image
              alt={images[activeIndex].alt}
              fill
              priority
              sizes="95vw"
              src={images[activeIndex].src}
            />
          </div>
          <figcaption>{images[activeIndex].caption}</figcaption>
        </figure>
      </dialog>
    </>
  );
}
