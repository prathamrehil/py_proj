import aspose.pdf as ap

document = ap.Document("ncert-textbook-for-class-11-maths-chapter-10.pdf")
artifactsToBeDeleted = []
for page in document.pages:
    for item in page.artifacts:
        if item.sub_type == ap.Artifact.artifact_subtype.WATERMARK:
            artifactsToBeDeleted.add(item)
    for item in artifactsToBeDeleted:
        page.artifacts.delete(item)

document.save("Output.pdf")
