import uuidv4 from 'uuid'
export const generateIdIfNotExist = (configObj) => {
  if (configObj.id) {
    return
  }
  // must add prefix id so easier using it with for DOM id. Some browsers do not allow DOM id with numeric started.
  configObj.id = 'id-' + uuidv4()
}
