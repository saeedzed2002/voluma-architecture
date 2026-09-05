"use client";

import Image from "next/image";
import { useRef, useState } from "react";

import { CloseIcon } from "./icons";

export type GalleryImage = {
  src: string;
  alt: string;
  caption: string;
};

type ProjectGalleryProps = {
  closeLabel: string;
  images: GalleryImage[];
  openLabel: string;
};

export function ProjectGallery({ closeLabel, images, openLabel }: ProjectGalleryProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const returnFocusRef = useRef<HTMLButtonElement | null>(null);
  const [activeIndex, setActiveIndex] = useState(0);

  const openImage = (index: number, trigger: HTMLButtonElement) => {
    setActiveIndex(index);
    returnFocusRef.current = trigger;
    dialogRef.current?.showModal();
  };

  const closeDialog = () => dialogRef.current?.close();

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
