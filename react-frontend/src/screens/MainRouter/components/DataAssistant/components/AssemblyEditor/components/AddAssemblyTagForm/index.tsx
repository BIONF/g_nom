import { Checkmark, Close, Trash } from "grommet-icons";
import { useEffect, useState } from "react";
import {
  addAssemblyTag,
  fetchAssemblyTagsByAssemblyID,
  INcbiTaxon,
  removeAssemblyTagbyTagID,
} from "../../../../../../../../api";
import Button from "../../../../../../../../components/Button";
import Input from "../../../../../../../../components/Input";
import { useNotification } from "../../../../../../../../components/NotificationProvider";
import {
  AssemblyInterface,
  AssemblyTagInterface,
} from "../../../../../../../../tsInterfaces/tsInterfaces";

const AddAssemblyTagForm = ({
  taxon,
  assembly,
}: {
  taxon: INcbiTaxon;
  assembly: AssemblyInterface;
}) => {
  const [tags, setTags] = useState<AssemblyTagInterface[]>();
  const [newAssemblyTag, setNewAssemblyTag] = useState<string>("");
  const [hoverTag, setHoverTag] = useState<number>(-1);
  const [removeTagConfirmation, setRemoveTagConfirmation] = useState<boolean>(false);

  // notifications
  const dispatch = useNotification();

  const handleNewNotification = (notification: any) => {
    dispatch({
      label: notification.label,
      message: notification.message,
      type: notification.type,
    });
  };

  useEffect(() => {
    loadTags();
  }, []);

  const loadTags = async () => {
    const userID = JSON.parse(sessionStorage.getItem("userID") || "{}");
    const token = JSON.parse(sessionStorage.getItem("token") || "{}");

    if (assembly && assembly.id && userID && token) {
      const response = await fetchAssemblyTagsByAssemblyID(assembly.id, userID, token);

      if (response && response.payload) {
        setTags(
          response.payload.map((tag) => ({
            ...tag,
            color: "#" + Math.random().toString(16).substr(-6),
          }))
        );
      }

      if (response && response.notification && response.notification.length > 0) {
        response.notification.map((not) => handleNewNotification(not));
      }
    }
  };

  const handleChangeNewAssemblyTag = (tag: string) => {
    const regex = /^([,.A-Za-z0-9_ ]*)$/g;
    if (!tag.match(regex)) {
      handleNewNotification({
        label: "Error",
        message: "Invalid input. No special characters allowed!",
        type: "error",
      });
    } else {
      setNewAssemblyTag(tag);
    }
  };

  const handleAddNewAssemblyTag = async () => {
    const regex = /^([,.A-Za-z0-9_ ]+)$/g;
    if (!newAssemblyTag.match(regex) && newAssemblyTag.length < 1) {
      handleNewNotification({
        label: "Error",
        message: "Invalid input. No special characters allowed!",
        type: "error",
      });
    } else {
      const userID = JSON.parse(sessionStorage.getItem("userID") || "{}");
      const token = JSON.parse(sessionStorage.getItem("token") || "{}");

      if (assembly && assembly.id && newAssemblyTag && userID && token) {
        if (!tags?.find((x) => x.tag.toUpperCase() === newAssemblyTag.toUpperCase())) {
          const response = await addAssemblyTag(
            assembly.id,
            newAssemblyTag.toUpperCase(),
            userID,
            token
          );

          if (response && response.notification && response.notification.length > 0) {
            response.notification.map((not) => handleNewNotification(not));
          }

          setNewAssemblyTag("");
          loadTags();
        } else {
          handleNewNotification({ label: "Info", message: "Tag already exists!", type: "info" });
        }
      } else {
        handleNewNotification({ label: "Error", message: "Missing input!", type: "error" });
      }
    }
  };

  const handleRemoveAssemblyTag = async (tag: AssemblyTagInterface) => {
    const userID = JSON.parse(sessionStorage.getItem("userID") || "{}");
    const token = JSON.parse(sessionStorage.getItem("token") || "{}");

    if (tag && tag.id && userID && token) {
      const response = await removeAssemblyTagbyTagID(tag.id, userID, token);

      if (response && response.notification && response.notification.length > 0) {
        response.notification.map((not) => handleNewNotification(not));
      }

      setRemoveTagConfirmation(false);
      setHoverTag(-1);
      loadTags();
    }
  };

  return (
    <div className="animate-grow-y">
      <div>
        <div className="grid grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-7 gap-4 justify-around py-2 border rounded mt-2 max-w-screen">
          {tags && tags.length > 0 ? (
            tags.map((tag, index) => (
              <div
                style={{ backgroundColor: tag.color }}
                className="text-white flex justify-center items-center py-1 rounded-lg uppercase font-semibold ring-1 ring-gray-400 ring-offset-1"
                onMouseEnter={() => setHoverTag(index)}
                onMouseLeave={() => {
                  setRemoveTagConfirmation(false);
                  setHoverTag(-1);
                }}
                onClick={() => setRemoveTagConfirmation(true)}
              >
                {hoverTag === index && !removeTagConfirmation && (
                  <div className="mr-4 flex items-center">
                    <Trash className="stroke-current" color="blank" size="small" />
                  </div>
                )}
                <span className="truncate w-24 text-center">
                  {!removeTagConfirmation ? tag.tag : "DELETE?"}
                </span>
                {hoverTag === index && removeTagConfirmation && (
                  <div className="flex items-center ml-8">
                    <div className="bg-green-600 text-white p-1 rounded-full flex items-center cursor-pointer hover:bg-green-400">
                      <Checkmark
                        className="stroke-current"
                        color="blank"
                        size="small"
                        onClick={() => handleRemoveAssemblyTag(tag)}
                      />
                    </div>
                    <div className="bg-red-600 text-white p-1 rounded-full flex items-center cursor-pointer hover:bg-red-400 ml-2">
                      <Close
                        className="stroke-current"
                        color="blank"
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          setRemoveTagConfirmation(false);
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="flex justify-center py-4">No items!</div>
          )}
        </div>
      </div>
      <hr className="shadow my-4" />
      <div className="flex">
        <label className="mx-4 flex items-center">
          <span className="w-32 font-semibold">New tag...</span>
          <Input
            placeholder="Max. 45 characters..."
            value={newAssemblyTag}
            onChange={(e) => handleChangeNewAssemblyTag(e.target.value)}
          />
        </label>
        <div className="mx-4 w-20">
          <Button label="Add" color="confirm" onClick={() => handleAddNewAssemblyTag()} />
        </div>
      </div>
    </div>
  );
};

export default AddAssemblyTagForm;
