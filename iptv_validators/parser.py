import re

from .models import M3UEntry


class M3UParser:
    """
    A robust parser for M3U and HLS playlists.
    """

    @staticmethod
    def parse(content: str) -> list[M3UEntry]:
        entries = []
        lines = content.splitlines()

        if not lines or not lines[0].startswith("#EXTM3U"):
            # Technically it should start with this, but we'll try to be tolerant.
            pass

        current_info: dict[str, str] = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("#EXTINF:"):
                # Example: #EXTINF:-1 tvg-id="Channel" tvg-name="Name" group-title="Group",Name
                current_info = {}
                # Extract metadata using regex
                # Regex to find key="value" or key=value
                metadata_matches = re.findall(r'([\w-]+)(?:=(?:"([^"]*)"|([^,\s]+)))?', line)
                for key, val_quoted, val_unquoted in metadata_matches:
                    val = val_quoted if val_quoted else val_unquoted
                    if val:
                        current_info[key] = val

                # The last part after the comma is the channel name
                if "," in line:
                    parts = line.split(",", 1)
                    if len(parts) > 1:
                        current_info["name"] = parts[1].strip()

            elif line.startswith("#EXT"):
                # Skip other #EXT tags for now, or handle them if needed.
                continue
            elif not line.startswith("#"):
                # This is a stream URL
                url = line

                # Construct M3UEntry
                entry = M3UEntry(
                    stream_url=url,
                    channel_name=current_info.get("name"),
                    tvg_id=current_info.get("tvg-id"),
                    tvg_name=current_info.get("tvg-name"),
                    tvg_logo=current_info.get("tvg-logo"),
                    group_title=current_info.get("group-title"),
                    extra_attributes={k: v for k, v in current_info.items() if k != "name"}
                )
                entries.append(entry)
                current_info = {}

        return entries

    @staticmethod
    def is_hls(content: str) -> bool:
        """
        Check if the content looks like an HLS playlist.
        """
        has_extm3u = "#EXTM3U" in content
        has_stream_inf = "#EXT-X-STREAM-INF" in content
        has_target_duration = "#EXT-X-TARGETDURATION" in content
        return has_extm3u and (has_stream_inf or has_target_duration)
