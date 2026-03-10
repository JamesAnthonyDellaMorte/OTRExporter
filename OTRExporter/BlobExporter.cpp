#include "BlobExporter.h"
#include "../ZAPD/ZFile.h"

void OTRExporter_Blob::Save(ZResource* res, const fs::path& outPath, BinaryWriter* writer)
{
	ZBlob* blob = (ZBlob*)res;
	
	WriteHeader(blob, outPath, writer, static_cast<uint32_t>(Ship::ResourceType::Blob));

	auto start = std::chrono::steady_clock::now();

	writer->Write((uint32_t)blob->GetRawDataSize());

	if (blob->parent != nullptr)
	{
		auto data = blob->parent->GetRawData();

		for (size_t i = blob->GetRawDataIndex(); i < blob->GetRawDataIndex() + blob->GetRawDataSize(); i++)
			writer->Write(data[i]);
	}
	else
	{
		const auto& data = blob->GetBlobData();
		for (size_t i = 0; i < data.size(); i++)
			writer->Write(data[i]);
	}

	auto end = std::chrono::steady_clock::now();
	size_t diff = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
}
