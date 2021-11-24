#! /usr/bin/env python3

import dataclasses
import datetime
import json
import operator
import pathlib
import sqlite3
import typing as t

import click


@dataclasses.dataclass(frozen=True)
class Creator:
    id_: int = dataclasses.field(repr=True)
    name: str = dataclasses.field(repr=True)
    first_name: str = dataclasses.field(repr=False)
    last_name: str = dataclasses.field(repr=False)
    url: str = dataclasses.field(repr=False)
    public_url: str = dataclasses.field(repr=False)
    thumbnail: str = dataclasses.field(repr=False)
    count_of_followers: int = dataclasses.field(repr=False)
    count_of_following: int = dataclasses.field(repr=False)
    count_of_designs: int = dataclasses.field(repr=False)
    accepts_tips: bool = dataclasses.field(repr=False)
    is_following: bool = dataclasses.field(repr=False)
    location: str = dataclasses.field(repr=False)
    cover: str = dataclasses.field(repr=False)

    @classmethod
    def load(cls, data: dict[str, t.Any]):
        return cls(
            id_=data["id"],
            name=data["name"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            url=data["url"],
            public_url=data["public_url"],
            thumbnail=data["thumbnail"],
            count_of_followers=data["count_of_followers"],
            count_of_following=data["count_of_following"],
            count_of_designs=data["count_of_designs"],
            accepts_tips=data["accepts_tips"],
            is_following=data["is_following"],
            location=data["location"],
            cover=data["cover"],
        )

    def as_tuple(self):
        return (
            self.id_,
            self.name,
            self.first_name,
            self.last_name,
        )


@dataclasses.dataclass(frozen=True)
class ImageSize:
    type_: str = dataclasses.field(repr=True)
    size: str = dataclasses.field(repr=False)
    url: str = dataclasses.field(repr=False)

    @classmethod
    def load_all(cls, items: list[dict[str, t.Any]]):
        return [cls.load(data) for data in items]

    @classmethod
    def load(cls, data: dict[str, t.Any]):
        return cls(
            type_=data["type"],
            size=data["size"],
            url=data["url"],
        )


@dataclasses.dataclass(frozen=True)
class Image:
    id_: int = dataclasses.field(repr=True)
    url: str = dataclasses.field(repr=False)
    name: str = dataclasses.field(repr=False)
    sizes: list[ImageSize] = dataclasses.field(repr=False)
    added: datetime.datetime = dataclasses.field(repr=False)

    @classmethod
    def load(cls, data: dict[str, t.Any]):
        if data is None:
            return None
        return cls(
            id_=data["id"],
            url=data["url"],
            name=data["name"],
            sizes=ImageSize.load_all(data["sizes"]),
            added=datetime.datetime.fromisoformat(data["added"]),
        )


@dataclasses.dataclass(frozen=True)
class DetailPartContent:
    caption: t.Optional[str] = dataclasses.field(repr=False)
    content: t.Optional[str] = dataclasses.field(repr=False)
    filament_brand: t.Optional[str] = dataclasses.field(repr=False)
    filament_color: t.Optional[str] = dataclasses.field(repr=False)
    filament_material: t.Optional[str] = dataclasses.field(repr=False)
    image: t.Optional[str] = dataclasses.field(repr=False)
    image_id: t.Optional[str] = dataclasses.field(repr=False)
    infill: t.Optional[str] = dataclasses.field(repr=False)
    notes: t.Optional[str] = dataclasses.field(repr=False)
    printer: t.Optional[str] = dataclasses.field(repr=False)
    printer_brand: t.Optional[str] = dataclasses.field(repr=False)
    rafts: t.Optional[str] = dataclasses.field(repr=False)
    resolution: t.Optional[str] = dataclasses.field(repr=False)
    supports: t.Optional[str] = dataclasses.field(repr=False)
    title: t.Optional[str] = dataclasses.field(repr=False)
    video: t.Optional[str] = dataclasses.field(repr=False)

    @classmethod
    def load_all(
        cls,
        items: t.Optional[
            t.Union[
                list[dict[str, t.Any]],
                list[str],
                dict[str, dict[str, t.Any]],
            ]
        ],
    ):
        if items is None:
            return None
        if isinstance(items, dict):
            sort_func = operator.itemgetter(0)
            field_func = operator.itemgetter(1)
            sorted_items = sorted(items.items(), key=sort_func)
            items = [*map(field_func, sorted_items)]
        return [cls.load(data) for data in items]

    @classmethod
    def load(cls, data: t.Union[dict[str, t.Any], str]):
        if isinstance(data, str):
            data = {"content": data}
        return cls(
            caption=data.get("caption"),
            content=data.get("content"),
            filament_brand=data.get("filament_brand"),
            filament_color=data.get("filament_color"),
            filament_material=data.get("filament_material"),
            image=data.get("image"),
            image_id=data.get("image_id"),
            infill=data.get("infill"),
            notes=data.get("notes"),
            printer=data.get("printer"),
            printer_brand=data.get("printer brand"),
            rafts=data.get("rafts"),
            resolution=data.get("resolution"),
            supports=data.get("supports"),
            title=data.get("title"),
            video=data.get("video"),
        )


@dataclasses.dataclass(frozen=True)
class DetailPart:
    type_: str = dataclasses.field(repr=True)
    name: str = dataclasses.field(repr=False)
    required: t.Optional[str] = dataclasses.field(repr=False)
    data: t.Optional[list[DetailPartContent]] = dataclasses.field(repr=False)

    @classmethod
    def load_all(cls, items: list[dict[str, t.Any]]):
        if items is None:
            return None
        return [cls.load(data) for data in items]

    @classmethod
    def load(cls, data: dict[str, t.Any]):
        return cls(
            type_=data["type"],
            name=data["name"],
            required=data.get("required"),
            data=DetailPartContent.load_all(data.get("data")),
        )


@dataclasses.dataclass(frozen=True)
class EducationDetailPart:
    type_: str = dataclasses.field(repr=True)
    name: str = dataclasses.field(repr=False)
    label: t.Optional[str] = dataclasses.field(repr=False)
    required: t.Optional[t.Union[str, bool]] = dataclasses.field(repr=False)
    save_as_component: t.Optional[bool] = dataclasses.field(repr=False)
    template: t.Optional[str] = dataclasses.field(repr=False)
    fieldname: t.Optional[str] = dataclasses.field(repr=False)
    default: t.Optional[str] = dataclasses.field(repr=False)
    data: t.Optional[list[DetailPartContent]] = dataclasses.field(repr=False)
    opts: t.Optional[dict[str, str]] = dataclasses.field(repr=False)

    @classmethod
    def load_all(cls, items: t.Optional[list[dict[str, t.Any]]]):
        if items is None:
            return None
        return [cls.load(data) for data in items]

    @classmethod
    def load(cls, data: dict[str, t.Any]):
        return cls(
            type_=data["type"],
            name=data["name"],
            label=data.get("label"),
            required=data.get("required"),
            save_as_component=data.get("save_as_component"),
            template=data.get("template"),
            fieldname=data.get("fieldname"),
            default=data.get("default"),
            data=DetailPartContent.load_all(data.get("data")),
            opts=data.get("opts"),
        )


@dataclasses.dataclass(frozen=True)
class Tag:
    name: str = dataclasses.field(repr=True)
    tag: str = dataclasses.field(repr=True)
    url: str = dataclasses.field(repr=False)
    count: int = dataclasses.field(repr=False)
    things_url: str = dataclasses.field(repr=False)
    absolute_url: str = dataclasses.field(repr=False)

    @classmethod
    def load_all(cls, items: t.Optional[list[dict[str, t.Any]]]):
        if items is None:
            return None
        return [cls.load(data) for data in items]

    @classmethod
    def load(cls, data: dict[str, t.Any]):
        return cls(
            name=data["name"],
            tag=data["tag"],
            url=data["url"],
            count=data["count"],
            things_url=data["things_url"],
            absolute_url=data["absolute_url"],
        )


@dataclasses.dataclass(frozen=True)
class EducationGrades:
    ...


@dataclasses.dataclass(frozen=True)
class EducationSubjects:
    id_: str = dataclasses.field(repr=True)
    name: str = dataclasses.field(repr=True)
    slug: str = dataclasses.field(repr=True)

    @classmethod
    def load_all(cls, items: t.Optional[list[dict[str, t.Any]]]):
        if items is None:
            return None
        return [cls.load(data) for data in items]

    @classmethod
    def load(cls, data: dict[str, t.Any]):
        return cls(
            id_=data["id"],
            name=data["name"],
            slug=data["slug"],
        )


@dataclasses.dataclass(frozen=True)
class Education:
    grades: list[dict] = dataclasses.field(repr=False)
    subjects: list[EducationSubjects] = dataclasses.field(repr=False)

    @classmethod
    def load(cls, data: dict[str, t.Any]):
        return cls(
            grades=data["grades"],
            subjects=EducationSubjects.load_all(data["subjects"]),
        )


@dataclasses.dataclass(frozen=True)
class Ancestor:
    id_: int = dataclasses.field(repr=True)

    @classmethod
    def load_all(cls, items: t.Optional[list[dict[str, t.Any]]]):
        if items is None:
            return None
        return [cls.load(data) for data in items]

    @classmethod
    def load(cls, data: dict[str, t.Any]):
        return cls(id_=data["id"])


@dataclasses.dataclass(frozen=True)
class Thing:
    id_: int = dataclasses.field(repr=True)
    name: str = dataclasses.field(repr=True)
    thumbnail: str = dataclasses.field(repr=False)
    url: str = dataclasses.field(repr=False)
    public_url: str = dataclasses.field(repr=False)
    creator: Creator = dataclasses.field(repr=False)
    added: datetime.datetime = dataclasses.field(repr=False)
    modified: datetime.datetime = dataclasses.field(repr=False)
    is_published: bool = dataclasses.field(repr=False)
    is_wip: bool = dataclasses.field(repr=False)
    is_featured: t.Optional[bool] = dataclasses.field(repr=False)
    is_nsfw: t.Optional[bool] = dataclasses.field(repr=False)
    like_count: int = dataclasses.field(repr=False)
    is_liked: bool = dataclasses.field(repr=False)
    collect_count: int = dataclasses.field(repr=False)
    is_collected: bool = dataclasses.field(repr=False)
    comment_count: int = dataclasses.field(repr=False)
    is_watched: bool = dataclasses.field(repr=False)
    default_image: t.Optional[Image] = dataclasses.field(repr=False)
    description: str = dataclasses.field(repr=False)
    instructions: str = dataclasses.field(repr=False)
    description_html: str = dataclasses.field(repr=False)
    instructions_html: str = dataclasses.field(repr=False)
    details: str = dataclasses.field(repr=False)
    details_parts: t.Optional[list[DetailPart]] = dataclasses.field(repr=False)
    edu_details: str = dataclasses.field(repr=False)
    edu_details_parts: t.Optional[list[EducationDetailPart]] = dataclasses.field(repr=False)
    license: str = dataclasses.field(repr=False)
    allows_derivatives: bool = dataclasses.field(repr=False)
    files_url: str = dataclasses.field(repr=False)
    images_url: str = dataclasses.field(repr=False)
    likes_url: str = dataclasses.field(repr=False)
    ancestors_url: str = dataclasses.field(repr=False)
    derivatives_url: str = dataclasses.field(repr=False)
    tags_url: str = dataclasses.field(repr=False)
    tags: t.Optional[list[Tag]] = dataclasses.field(repr=False)
    categories_url: str = dataclasses.field(repr=False)
    file_count: int = dataclasses.field(repr=False)
    layout_count: int = dataclasses.field(repr=False)
    layouts_url: str = dataclasses.field(repr=False)
    is_private: bool = dataclasses.field(repr=False)
    is_purchased: bool = dataclasses.field(repr=False)
    in_library: bool = dataclasses.field(repr=False)
    print_history_count: int = dataclasses.field(repr=False)
    app_id: t.Optional[str] = dataclasses.field(repr=False)
    download_count: int = dataclasses.field(repr=False)
    view_count: int = dataclasses.field(repr=False)
    education: Education = dataclasses.field(repr=False)
    remix_count: int = dataclasses.field(repr=False)
    make_count: int = dataclasses.field(repr=False)
    app_count: int = dataclasses.field(repr=False)
    root_comment_count: int = dataclasses.field(repr=False)
    moderation: str = dataclasses.field(repr=False)
    is_derivative: bool = dataclasses.field(repr=False)
    ancestors: t.Optional[list[Ancestor]] = dataclasses.field(repr=False)
    can_comment: bool = dataclasses.field(repr=False)

    @classmethod
    def load(cls, data: dict[str, t.Any]):
        return cls(
            id_=data["id"],
            name=data["name"],
            thumbnail=data["thumbnail"],
            url=data["url"],
            public_url=data["public_url"],
            creator=Creator.load(data["creator"]),
            added=data["added"],
            modified=data["modified"],
            is_published=data["is_published"],
            is_wip=data["is_wip"],
            is_featured=data.get("is_featured"),
            is_nsfw=data["is_nsfw"],
            like_count=data["like_count"],
            is_liked=data["is_liked"],
            collect_count=data["collect_count"],
            is_collected=data["is_collected"],
            comment_count=data["comment_count"],
            is_watched=data["is_watched"],
            default_image=Image.load(data["default_image"]),
            description=data["description"],
            instructions=data["instructions"],
            description_html=data["description_html"],
            instructions_html=data["instructions_html"],
            details=data["details"],
            details_parts=DetailPart.load_all(data["details_parts"]),
            edu_details=data["edu_details"],
            edu_details_parts=EducationDetailPart.load_all(data["edu_details_parts"]),
            license=data["license"],
            allows_derivatives=data["allows_derivatives"],
            files_url=data["files_url"],
            images_url=data["images_url"],
            likes_url=data["likes_url"],
            ancestors_url=data["ancestors_url"],
            derivatives_url=data["derivatives_url"],
            tags_url=data["tags_url"],
            tags=Tag.load_all(data["tags"]),
            categories_url=data["categories_url"],
            file_count=data["file_count"],
            layout_count=data["layout_count"],
            layouts_url=data["layouts_url"],
            is_private=data["is_private"],
            is_purchased=data["is_purchased"],
            in_library=data["in_library"],
            print_history_count=data["print_history_count"],
            app_id=data["app_id"],
            download_count=data["download_count"],
            view_count=data["view_count"],
            education=Education.load(data["education"]),
            remix_count=data["remix_count"],
            make_count=data["make_count"],
            app_count=data["app_count"],
            root_comment_count=data["root_comment_count"],
            moderation=data["moderation"],
            is_derivative=data["is_derivative"],
            ancestors=Ancestor.load_all(data["ancestors"]),
            can_comment=data["can_comment"],
        )

    def as_tuple(self):
        return (
            self.id_,
            self.name,
            self.creator.id_,
            self.default_image.id_ if self.default_image else None,
            self.description,
        )


@click.command(name="thingiverse")
@click.argument("src_dirs", nargs=-1)
def main(src_dirs: list[str]):
    creator_id_saved: set[str] = set()
    conn = sqlite3.connect("items.db")
    conn.execute(CREATE_THING_TABLE)
    conn.execute(CREATE_CREATOR_TABLE)
    for item in load_all(src_dirs):
        conn.execute(INSERT_THING, item.as_tuple())
        if item.creator.id_ not in creator_id_saved:
            conn.execute(INSERT_CREATOR, item.creator.as_tuple())
            creator_id_saved.add(item.creator.id_)
    conn.commit()


# @click.command(name="thingiverse")
# @click.argument("src_dirs", nargs=-1)
# def main(src_dirs: list[str]):
#     for item in load_all(src_dirs):
#         print(item, sep="")
#         print("\t", item.creator, sep="")
#         print("\t", item.default_image, sep="")
#         if item.details_parts:
#             for part in item.details_parts:
#                 print("\t\t", part, sep="")
#         if item.edu_details_parts:
#             for part in item.edu_details_parts:
#                 print("\t\t", part, sep="")
#         if item.tags:
#             for tag in item.tags:
#                 print("\t\t", tag, sep="")
#         print("\t", item.education, sep="")
#         print("\t", item.ancestors, sep="")


def load_all(src_dirs: list[str]):
    for src_dir in src_dirs:
        if (p := pathlib.Path(src_dir)).is_dir():
            for item in p.rglob("*.json"):
                with item.open(mode="r") as f:
                    data = json.load(f)
                    if "id" in data:
                        yield Thing.load(data)


CREATE_THING_TABLE = """
CREATE TABLE IF NOT EXISTS thing (
    id INTEGER PRIMARY KEY,
    name STRING NOT NULL,
    creator_id INTEGER NOT NULL,
    default_image_id INTEGER,
    description STRING NOT NULL,
) WITHOUT ROWID
"""


CREATE_CREATOR_TABLE = """
CREATE TABLE IF NOT EXISTS creator (
    id INTEGER PRIMARY KEY,
    name STRING NOT NULL,
    first_name STRING NOT NULL,
    last_name STRING NOT NULL
) WITHOUT ROWID
"""

INSERT_THING = """
INSERT INTO thing
(
    id,
    name,
    thumbnail,
    url,
    public_url,
    creator_id,
    added,
    modified,
    is_published,
    is_wip,
    is_featured,
    is_nsfw,
    like_count,
    is_liked,
    collect_count,
    is_collected,
    comment_count,
    is_watched,
    default_image_id,
    description,
    instructions,
    description_html,
    instructions_html,
    details,
    edu_details,
    license,
    allows_derivatives,
    files_url,
    images_url,
    likes_url,
    ancestors_url,
    derivatives_url,
    tags_url,
    categories_url,
    file_count,
    layout_count,
    layouts_url,
    is_private,
    is_purchased,
    in_library,
    print_history_count,
    app_id,
    download_count,
    view_count,
    remix_count,
    make_count,
    app_count,
    root_comment_count,
    moderation,
    is_derivative,
    can_comment
)
VALUES
(
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?
)
"""


INSERT_CREATOR = """INSERT INTO creator ( id, name, first_name, last_name) VALUES ( ?, ?, ?, ?)"""


if __name__ == "__main__":
    main()
