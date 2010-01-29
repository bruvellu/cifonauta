#!/bin/bash

THUMBS=$2

if [ ! -d "$THUMBS" ]; then
	mkdir "$THUMBS"
	mkdir "$THUMBS"/100px
	mkdir "$THUMBS"/250px
	mkdir "$THUMBS"/300px
	mkdir "$THUMBS"/400px
	mkdir "$THUMBS"/450px
	mkdir "$THUMBS"/500px
fi

echo Criando thumbnails... de $1

cp "$1" "$THUMBS"/100px;
cp "$1" "$THUMBS"/250px;
cp "$1" "$THUMBS"/300px;
cp "$1" "$THUMBS"/400px;
cp "$1" "$THUMBS"/450px;
cp "$1" "$THUMBS"/500px;

echo Copiada. Redimensionando...
mogrify -resize "100>" -format jpg -quality 60 "$THUMBS"/100px/`basename "$1"`
mogrify -resize "250>" -format jpg -quality 60 "$THUMBS"/250px/`basename "$1"`
mogrify -resize "300>" -format jpg -quality 60 "$THUMBS"/300px/`basename "$1"`
mogrify -resize "400>" -format jpg -quality 60 "$THUMBS"/400px/`basename "$1"`
mogrify -resize "450>" -format jpg -quality 60 "$THUMBS"/450px/`basename "$1"`
mogrify -resize "500>" -format jpg -quality 60 "$THUMBS"/500px/`basename "$1"`

echo Pronto.
